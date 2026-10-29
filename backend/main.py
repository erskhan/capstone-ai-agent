"""FastAPI application entry point."""

import uuid
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session

from shared.config import get_settings
from shared.logger import setup_logging, get_logger
from database.db import init_db, get_db
from models.schemas import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    ApplicationStatus,
    ErrorResponse,
    PaginationParams,
    ApplicationListResponse,
)
from agents.orchestrator import LoanApprovalOrchestrator
from backend.db_service import WorkflowStateService

logger = get_logger("main")
settings = get_settings()

# Initialize orchestrator
orchestrator = LoanApprovalOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting up application...")
    setup_logging()
    init_db()
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title="Loan Approval System API",
    description="Agentic AI Intelligent Loan Approval System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
    }


async def _process_application_async(
    application_id: str,
    correlation_id: str,
    request: LoanApplicationRequest,
):
    """Background task to process application through orchestrator."""
    try:
        logger.info(
            f"Background: Starting orchestration for {application_id}",
            extra={"correlation_id": correlation_id},
        )

        # Run async orchestrator
        result = await orchestrator.process_application_async(
            application=request,
            application_id=application_id,
            correlation_id=correlation_id,
        )

        logger.info(
            f"Background: Orchestration completed for {application_id}",
            extra={"correlation_id": correlation_id, "decision": result.get("decision", {}).get("classification_value")},
        )

    except Exception as e:
        logger.error(
            f"Background: Orchestration failed for {application_id}: {str(e)}",
            extra={"correlation_id": correlation_id},
            exc_info=True,
        )


@app.post(
    "/api/applications",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Applications"],
)
async def submit_application(
    request: LoanApplicationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Submit a new loan application and start async processing."""
    try:
        application_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())

        logger.info(
            "Received loan application",
            extra={
                "application_id": application_id,
                "correlation_id": correlation_id,
            },
        )

        from database.models import LoanApplicationModel

        db_application = LoanApplicationModel(
            id=application_id,
            status=ApplicationStatus.SUBMITTED.value,
            correlation_id=correlation_id,
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)

        # Create workflow execution record
        WorkflowStateService.create_workflow_execution(db, application_id, correlation_id)

        # Log audit entry
        WorkflowStateService.log_audit(
            db,
            application_id,
            correlation_id,
            "application_submitted",
            details={"loan_amount": request.loan_details.loan_amount},
        )

        # Start async orchestration in background
        background_tasks.add_task(
            _process_application_async,
            application_id,
            correlation_id,
            request,
        )

        logger.info(
            f"Queued orchestration for {application_id}",
            extra={"correlation_id": correlation_id},
        )

        return LoanApplicationResponse(
            application_id=application_id,
            status=ApplicationStatus.SUBMITTED,
            submitted_at=db_application.submitted_at,
            updated_at=db_application.updated_at,
        )
    except Exception as e:
        logger.error(f"Error submitting application: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit application",
        )


@app.get(
    "/api/applications/{application_id}",
    response_model=LoanApplicationResponse,
    tags=["Applications"],
)
async def get_application(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Get application status by ID."""
    from database.models import LoanApplicationModel

    application = db.query(LoanApplicationModel).filter_by(id=application_id).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found",
        )

    return LoanApplicationResponse(
        application_id=application.id,
        status=ApplicationStatus(application.status),
        submitted_at=application.submitted_at,
        updated_at=application.updated_at,
    )


@app.get(
    "/api/applications",
    response_model=ApplicationListResponse,
    tags=["Applications"],
)
async def list_applications(
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    """List all loan applications with pagination."""
    from database.models import LoanApplicationModel

    query = db.query(LoanApplicationModel)
    total = query.count()

    applications = (
        query.offset(params.skip)
        .limit(params.limit)
        .all()
    )

    return ApplicationListResponse(
        total=total,
        skip=params.skip,
        limit=params.limit,
        applications=[
            LoanApplicationResponse(
                application_id=app.id,
                status=ApplicationStatus(app.status),
                submitted_at=app.submitted_at,
                updated_at=app.updated_at,
            )
            for app in applications
        ],
    )


@app.get(
    "/api/applications/{application_id}/workflow-state",
    tags=["Workflow"],
)
async def get_workflow_state(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Get workflow execution state for an application."""
    try:
        state_summary = WorkflowStateService.get_workflow_state_summary(db, application_id)

        if not state_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow not found for application {application_id}",
            )

        return state_summary

    except Exception as e:
        logger.error(f"Error retrieving workflow state: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow state",
        )


@app.get(
    "/api/applications/{application_id}/workflow-execution",
    tags=["Workflow"],
)
async def get_workflow_execution(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Get full workflow execution details for an application."""
    try:
        execution_details = WorkflowStateService.get_workflow_execution_details(db, application_id)

        if not execution_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution not found for application {application_id}",
            )

        return execution_details

    except Exception as e:
        logger.error(f"Error retrieving workflow execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow execution",
        )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle value errors."""
    return ErrorResponse(
        error_code="VALIDATION_ERROR",
        message=str(exc),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.api_workers,
    )
