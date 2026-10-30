"""Additional API schemas for appeal, audit trail, and decision endpoints."""

from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class DecisionDetailResponse(BaseModel):
    """Full decision details response."""

    classification: str = Field(..., description="Decision classification (approved/rejected/manual_review)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    reasoning: str = Field(..., description="Reasoning for decision")
    decision_factors: Dict[str, Any] = Field(default_factory=dict, description="Positive and negative factors")
    recommended_rate: Optional[float] = Field(None, ge=0, le=30, description="Recommended interest rate")
    approved_loan_amount: Optional[float] = Field(None, gt=0, description="Approved loan amount")
    conditions: Optional[List[str]] = Field(None, description="Loan conditions")
    compliance_notes: Optional[str] = Field(None, description="Compliance validation notes")


class AppealRequest(BaseModel):
    """Appeal submission request."""

    application_id: str = Field(..., description="Application ID to appeal")
    appeal_reason: str = Field(..., min_length=10, max_length=2000, description="Reason for appeal")
    additional_documentation: Optional[str] = Field(None, max_length=5000, description="Additional supporting info")
    contact_email: Optional[str] = Field(None, description="Contact email for appeal")
    contact_phone: Optional[str] = Field(None, description="Contact phone for appeal")


class AppealResponse(BaseModel):
    """Appeal submission response."""

    appeal_id: str = Field(..., description="Unique appeal ID")
    application_id: str = Field(..., description="Associated application ID")
    status: str = Field(..., description="Appeal status (received/pending/approved/rejected)")
    submitted_at: datetime = Field(..., description="When appeal was submitted")
    expected_decision_date: Optional[datetime] = Field(None, description="Expected decision date")
    message: str = Field(..., description="Status message")


class AuditLogEntry(BaseModel):
    """Single audit log entry."""

    timestamp: datetime = Field(..., description="When action occurred")
    action: str = Field(..., description="Action performed")
    agent_name: Optional[str] = Field(None, description="Agent that performed action")
    details: Dict[str, Any] = Field(default_factory=dict, description="Action details")


class AuditTrailResponse(BaseModel):
    """Complete audit trail for an application."""

    application_id: str = Field(..., description="Application ID")
    total_entries: int = Field(..., ge=0, description="Total audit entries")
    entries: List[AuditLogEntry] = Field(default_factory=list, description="Audit entries")
    earliest_entry: Optional[datetime] = Field(None, description="Earliest entry timestamp")
    latest_entry: Optional[datetime] = Field(None, description="Latest entry timestamp")


class ManualReviewRequest(BaseModel):
    """Request to assign application to manual review."""

    application_id: str = Field(..., description="Application ID")
    reason: str = Field(..., min_length=10, max_length=1000, description="Reason for manual review")
    assigned_to: Optional[str] = Field(None, description="Reviewer name or ID")
    priority: str = Field("normal", regex="^(low|normal|high|urgent)$", description="Review priority")


class ManualReviewResponse(BaseModel):
    """Manual review assignment response."""

    application_id: str = Field(..., description="Application ID")
    review_id: str = Field(..., description="Unique review ID")
    status: str = Field(..., description="Review status")
    assigned_at: datetime = Field(..., description="When assigned")
    assigned_to: Optional[str] = Field(None, description="Assigned reviewer")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion date")


class HealthCheckDetailed(BaseModel):
    """Detailed health check response."""

    status: str = Field(..., description="Overall system status (healthy/degraded/unhealthy)")
    timestamp: datetime = Field(..., description="Check timestamp")
    services: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Status of each service component",
    )
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., ge=0, description="Uptime in seconds")


class WorkflowStateResponse(BaseModel):
    """Workflow state response."""

    execution_id: str = Field(..., description="Workflow execution ID")
    application_id: str = Field(..., description="Application ID")
    workflow_state: str = Field(..., description="Current workflow state")
    current_step: str = Field(..., description="Current step in workflow")
    attempt_number: int = Field(..., ge=1, le=3, description="Attempt number")
    started_at: Optional[datetime] = Field(None, description="When workflow started")
    completed_at: Optional[datetime] = Field(None, description="When workflow completed")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_step: Optional[str] = Field(None, description="Step where error occurred")


class BatchApplicationRequest(BaseModel):
    """Request to process multiple applications."""

    application_ids: List[str] = Field(..., min_items=1, max_items=100, description="Application IDs to process")
    action: str = Field(..., regex="^(approve|reject|review)$", description="Action to perform")
    reason: Optional[str] = Field(None, max_length=1000, description="Reason for batch action")


class BatchApplicationResponse(BaseModel):
    """Response for batch application processing."""

    batch_id: str = Field(..., description="Batch operation ID")
    total: int = Field(..., ge=0, description="Total applications in batch")
    processed: int = Field(..., ge=0, description="Successfully processed")
    failed: int = Field(..., ge=0, description="Failed applications")
    status: str = Field(..., description="Batch status (processing/completed/failed)")
    details: List[Dict[str, Any]] = Field(default_factory=list, description="Per-application details")


class StatisticsResponse(BaseModel):
    """System statistics response."""

    date: str = Field(..., description="Statistics date (YYYY-MM-DD)")
    total_applications: int = Field(..., ge=0, description="Total applications processed")
    approved: int = Field(..., ge=0, description="Approved applications")
    rejected: int = Field(..., ge=0, description="Rejected applications")
    under_review: int = Field(..., ge=0, description="Under review applications")
    approval_rate: float = Field(..., ge=0, le=100, description="Approval percentage")
    average_processing_time_seconds: float = Field(..., ge=0, description="Average processing time")
    average_risk_score: float = Field(..., ge=0, le=100, description="Average risk score")
    manual_reviews: int = Field(..., ge=0, description="Manual review requests")
    appeals: int = Field(..., ge=0, description="Appeal submissions")
