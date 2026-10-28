"""Pydantic schemas for request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Any

from pydantic import BaseModel, EmailStr, Field


class ApplicationStatus(str, Enum):
    """Application processing status."""

    SUBMITTED = "submitted"
    VALIDATING = "validating"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"
    APPEALED = "appealed"


class DecisionClassification(str, Enum):
    """Loan decision classification."""

    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class EmploymentType(str, Enum):
    """Type of employment."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    SELF_EMPLOYED = "self_employed"
    RETIRED = "retired"
    STUDENT = "student"
    UNEMPLOYED = "unemployed"


# Request Models
class ApplicantProfile(BaseModel):
    """Applicant profile information."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    date_of_birth: str = Field(..., description="YYYY-MM-DD format")
    ssn: str = Field(..., min_length=9, max_length=11, description="Social Security Number")
    address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., min_length=5, max_length=10)


class EmploymentInfo(BaseModel):
    """Employment information."""

    employment_type: EmploymentType
    employer_name: str = Field(..., min_length=1, max_length=200)
    job_title: str = Field(..., min_length=1, max_length=100)
    years_employed: float = Field(..., ge=0, le=70)
    annual_income: float = Field(..., gt=0)
    monthly_income: Optional[float] = Field(None, gt=0)


class CreditRecord(BaseModel):
    """Credit history information."""

    credit_score: int = Field(..., ge=300, le=850)
    years_of_credit_history: float = Field(..., ge=0, le=80)
    number_of_accounts: int = Field(..., ge=0)
    delinquencies_last_24_months: int = Field(..., ge=0)
    public_records: int = Field(..., ge=0)
    current_debt: float = Field(..., ge=0)


class LoanDetails(BaseModel):
    """Loan request details."""

    loan_amount: float = Field(..., gt=0, le=10000000)
    loan_purpose: str = Field(..., min_length=1, max_length=200)
    loan_term_months: int = Field(..., ge=6, le=360)
    interest_rate: Optional[float] = Field(None, ge=0, le=30)


class LoanApplicationRequest(BaseModel):
    """Loan application submission request."""

    applicant_profile: ApplicantProfile
    employment_info: EmploymentInfo
    credit_record: CreditRecord
    loan_details: LoanDetails
    additional_notes: Optional[str] = Field(None, max_length=1000)


# Response Models
class RiskAssessment(BaseModel):
    """Risk assessment details."""

    debt_to_income_ratio: float
    dti_risk_level: str  # low, medium, high
    credit_score_risk_level: str  # low, medium, high
    anomalies_detected: List[str] = []
    overall_risk_score: float = Field(..., ge=0, le=100)
    assessed_at: datetime


class LoanDecision(BaseModel):
    """Loan decision details."""

    classification: DecisionClassification
    confidence_score: float = Field(..., ge=0, le=1)
    risk_factors: List[str] = []
    positive_factors: List[str] = []
    reasoning: str
    recommended_interest_rate: Optional[float] = None
    conditions: List[str] = []
    appeals_available: bool = True


class DecisionResponse(BaseModel):
    """Decision response with all details."""

    classification: DecisionClassification
    confidence_score: float
    reasoning: str
    risk_assessment: RiskAssessment
    recommended_interest_rate: Optional[float] = None


class AuditLogEntry(BaseModel):
    """Single audit log entry."""

    action: str
    agent_name: Optional[str] = None
    details: dict = {}
    timestamp: datetime
    correlation_id: str


class AuditLogResponse(BaseModel):
    """Audit log response."""

    application_id: str
    entries: List[AuditLogEntry]


class LoanApplicationResponse(BaseModel):
    """Loan application response with current status."""

    application_id: str
    status: ApplicationStatus
    submitted_at: datetime
    updated_at: datetime
    decision: Optional[DecisionResponse] = None
    audit_trail: List[AuditLogEntry] = []


class ErrorResponse(BaseModel):
    """Standard error response."""

    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class ApplicationListResponse(BaseModel):
    """Paginated list of applications."""

    total: int
    skip: int
    limit: int
    applications: List[LoanApplicationResponse]
