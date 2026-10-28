"""FastAPI application entry point."""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
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

logger = get_logger("main")
settings = get_settings()


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


@app.post(
    "/api/applications",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Applications"],
)
async def submit_application(
    request: LoanApplicationRequest,
    db: Session = Depends(get_db),
):
    """Submit a new loan application."""
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
