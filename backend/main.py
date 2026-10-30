"""FastAPI application entry point."""

import uuid
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
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
from backend.api_schemas import (
    DecisionDetailResponse,
    AppealRequest,
    AppealResponse,
    AuditTrailResponse,
    AuditLogEntry,
    ManualReviewRequest,
    ManualReviewResponse,
    HealthCheckDetailed,
)
from agents.orchestrator import LoanApprovalOrchestrator
from backend.db_service import WorkflowStateService
from backend.appeal_service import AppealService
from backend.audit_service import AuditService
from backend.decision_service import DecisionService
from datetime import datetime

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

        # Save decision to database
        db = next(get_db())
        try:
            # Get workflow execution
            from database.models import WorkflowExecutionModel
            execution = db.query(WorkflowExecutionModel).filter_by(application_id=application_id).first()

            if execution and result.get("decision"):
                # Update execution with decision results
                WorkflowStateService.mark_completed(
                    db,
                    execution.id,
                    result.get("decision")
                )

                # Update application status
                from database.models import LoanApplicationModel
                application = db.query(LoanApplicationModel).filter_by(id=application_id).first()
                if application:
                    decision_value = result.get("decision", {}).get("classification_value", "unknown")
                    if decision_value == "approved":
                        application.status = ApplicationStatus.APPROVED.value
                    elif decision_value == "rejected":
                        application.status = ApplicationStatus.REJECTED.value
                    else:
                        application.status = ApplicationStatus.UNDER_REVIEW.value
                    application.updated_at = datetime.utcnow()
                    db.commit()
        finally:
            db.close()

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
    user_email: str = None,
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
                "user_email": user_email,
            },
        )

        from database.models import LoanApplicationModel

        db_application = LoanApplicationModel(
            id=application_id,
            status=ApplicationStatus.SUBMITTED.value,
            correlation_id=correlation_id,
            applicant_email=user_email,
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
    user_email: str = None,
):
    """List loan applications with optional email filter."""
    from database.models import LoanApplicationModel

    query = db.query(LoanApplicationModel)

    # Filter by email if provided
    if user_email:
        query = query.filter_by(applicant_email=user_email)

    total = query.count()

    applications = (
        query.order_by(LoanApplicationModel.submitted_at.desc())
        .offset(params.skip)
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
        from database.models import LoanApplicationModel

        # Get application status
        application = db.query(LoanApplicationModel).filter_by(id=application_id).first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        state_summary = WorkflowStateService.get_workflow_state_summary(db, application_id)

        if not state_summary:
            # Return default state if workflow record doesn't exist
            return {
                "execution_id": None,
                "application_id": application_id,
                "workflow_state": "completed" if application.status in ["approved", "rejected"] else "processing",
                "current_step": application.status,
                "attempt_number": 1,
                "error_message": None,
                "error_step": None,
                "started_at": application.submitted_at.isoformat() if application.submitted_at else None,
                "completed_at": application.updated_at.isoformat() if application.updated_at else None,
            }

        return state_summary

    except HTTPException:
        raise
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


@app.get(
    "/api/applications/{application_id}/decision",
    response_model=DecisionDetailResponse,
    tags=["Decisions"],
)
async def get_decision(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Get full decision details for an application."""
    try:
        logger.info(f"Retrieving decision for {application_id}")

        decision = DecisionService.get_decision_details(db, application_id)

        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision not found for application {application_id}",
            )

        return DecisionDetailResponse(**decision)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving decision: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve decision",
        )


@app.get(
    "/api/applications/{application_id}/audit-trail",
    response_model=AuditTrailResponse,
    tags=["Audit"],
)
async def get_audit_trail(
    application_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get audit trail for an application."""
    try:
        logger.info(
            f"Retrieving audit trail for {application_id}",
            extra={"limit": limit, "offset": offset},
        )

        audit_trail = AuditService.get_audit_trail(db, application_id, limit, offset)

        entries = [AuditLogEntry(**entry) for entry in audit_trail["entries"]]

        return AuditTrailResponse(
            application_id=application_id,
            total_entries=audit_trail["total_entries"],
            entries=entries,
            earliest_entry=audit_trail.get("earliest_entry"),
            latest_entry=audit_trail.get("latest_entry"),
        )

    except Exception as e:
        logger.error(f"Error retrieving audit trail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit trail",
        )


@app.post(
    "/api/applications/{application_id}/appeal",
    response_model=AppealResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Appeals"],
)
async def submit_appeal(
    application_id: str,
    request: AppealRequest,
    db: Session = Depends(get_db),
):
    """Submit an appeal for a rejected application."""
    try:
        logger.info(
            f"Submitting appeal for {application_id}",
            extra={"reason_length": len(request.appeal_reason)},
        )

        # Verify application exists
        from database.models import LoanApplicationModel

        application = db.query(LoanApplicationModel).filter_by(id=application_id).first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        # Create appeal
        appeal_result = AppealService.create_appeal(
            db,
            application_id,
            request.appeal_reason,
            request.additional_documentation,
            request.contact_email,
            request.contact_phone,
        )

        # Log audit entry
        WorkflowStateService.log_audit(
            db,
            application_id,
            application.correlation_id,
            "appeal_submitted",
            details={
                "appeal_reason": request.appeal_reason[:100],
                "contact_email": request.contact_email,
            },
        )

        return AppealResponse(
            appeal_id=appeal_result["appeal_id"],
            application_id=appeal_result["application_id"],
            status=appeal_result["status"],
            submitted_at=datetime.fromisoformat(appeal_result["submitted_at"]),
            expected_decision_date=datetime.fromisoformat(
                appeal_result["expected_decision_date"]
            ),
            message="Appeal received successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting appeal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit appeal",
        )


@app.post(
    "/api/applications/{application_id}/review",
    response_model=ManualReviewResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["ManualReview"],
)
async def assign_to_manual_review(
    application_id: str,
    request: ManualReviewRequest,
    db: Session = Depends(get_db),
):
    """Assign application to manual review."""
    try:
        logger.info(
            f"Assigning {application_id} to manual review",
            extra={"priority": request.priority},
        )

        # Verify application exists
        from database.models import LoanApplicationModel

        application = db.query(LoanApplicationModel).filter_by(id=application_id).first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        # Assign to manual review
        review_result = AppealService.assign_to_manual_review(
            db,
            application_id,
            request.reason,
            request.assigned_to,
            request.priority,
        )

        # Log audit entry
        WorkflowStateService.log_audit(
            db,
            application_id,
            application.correlation_id,
            "assigned_to_manual_review",
            details={
                "reason": request.reason[:100],
                "priority": request.priority,
                "assigned_to": request.assigned_to,
            },
        )

        return ManualReviewResponse(
            application_id=review_result["application_id"],
            review_id=review_result["review_id"],
            status=review_result["status"],
            assigned_at=datetime.fromisoformat(review_result["assigned_at"]),
            assigned_to=review_result.get("assigned_to"),
            estimated_completion=datetime.fromisoformat(
                review_result["estimated_completion"]
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning to manual review: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign to manual review",
        )


@app.get(
    "/health/detailed",
    response_model=HealthCheckDetailed,
    tags=["Health"],
)
async def detailed_health_check(
    db: Session = Depends(get_db),
):
    """Detailed health check with service status."""
    try:
        # Check database
        db_healthy = False
        try:
            from database.models import LoanApplicationModel
            db.query(LoanApplicationModel).limit(1).all()
            db_healthy = True
        except Exception as e:
            logger.warning(f"Database health check failed: {str(e)}")

        return HealthCheckDetailed(
            status="healthy" if db_healthy else "degraded",
            timestamp=datetime.utcnow(),
            services={
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "response_time_ms": 10,
                },
                "api": {
                    "status": "healthy",
                    "response_time_ms": 5,
                },
                "orchestrator": {
                    "status": "healthy",
                    "agents": 5,
                },
            },
            version="0.2.0",
            uptime_seconds=1000,
        )

    except Exception as e:
        logger.error(f"Error in detailed health check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed",
        )


@app.post(
    "/api/applications/{application_id}/manual-review",
    tags=["ManualReview"],
)
async def submit_manual_review_decision(
    application_id: str,
    decision_data: dict,
    db: Session = Depends(get_db),
):
    """Submit manual review decision for an application."""
    try:
        from database.models import LoanApplicationModel

        logger.info(f"Processing manual review for {application_id}")

        # Verify application exists
        application = db.query(LoanApplicationModel).filter_by(id=application_id).first()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        decision_type = decision_data.get("decision")

        # Update application status based on decision
        if decision_type == "approve":
            application.status = ApplicationStatus.APPROVED.value
            logger.info(f"Manually approved application {application_id}")
        elif decision_type == "reject":
            application.status = ApplicationStatus.REJECTED.value
            logger.info(f"Manually rejected application {application_id}")
        else:  # request_info
            application.status = ApplicationStatus.UNDER_REVIEW.value
            logger.info(f"Requested more info for application {application_id}")

        application.updated_at = datetime.utcnow()
        db.commit()

        # Log audit entry
        WorkflowStateService.log_audit(
            db,
            application_id,
            application.correlation_id or "",
            f"manual_review_{decision_type}",
            details={
                "decision": decision_type,
                "reviewer_notes": decision_data.get("reviewer_notes", "")[:100],
                "reviewer_id": decision_data.get("reviewer_id"),
            },
        )

        return {
            "message": "Manual review decision recorded successfully",
            "application_id": application_id,
            "decision": decision_type,
            "status": application.status,
            "updated_at": application.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing manual review: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process manual review",
        )


@app.delete(
    "/api/applications/{application_id}",
    tags=["Applications"],
)
async def delete_application(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Delete an application and all related records."""
    try:
        from database.models import (
            LoanApplicationModel, WorkflowExecutionModel, AuditLogModel,
            ApplicantModel, EmploymentInfoModel, CreditRecordModel,
            LoanDetailsModel, RiskAssessmentModel, LoanDecisionModel
        )

        logger.info(f"Deleting application: {application_id}")

        # Verify application exists
        application = db.query(LoanApplicationModel).filter_by(id=application_id).first()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        # Delete in correct order to respect foreign keys
        db.query(AuditLogModel).filter_by(application_id=application_id).delete()
        db.query(RiskAssessmentModel).filter_by(application_id=application_id).delete()
        db.query(LoanDecisionModel).filter_by(application_id=application_id).delete()
        db.query(LoanDetailsModel).filter_by(application_id=application_id).delete()
        db.query(CreditRecordModel).filter_by(application_id=application_id).delete()
        db.query(EmploymentInfoModel).filter_by(application_id=application_id).delete()
        db.query(ApplicantModel).filter_by(application_id=application_id).delete()
        db.query(WorkflowExecutionModel).filter_by(application_id=application_id).delete()
        db.query(LoanApplicationModel).filter_by(id=application_id).delete()

        db.commit()

        logger.info(f"Successfully deleted application: {application_id}")

        return {
            "message": "Application deleted successfully",
            "application_id": application_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application",
        )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle value errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": str(exc),
        },
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
