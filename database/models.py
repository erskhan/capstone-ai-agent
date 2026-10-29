"""SQLAlchemy ORM models for database tables."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from database.db import Base


class LoanApplicationModel(Base):
    """Loan application model."""

    __tablename__ = "loan_applications"

    id = Column(String(36), primary_key=True, index=True)
    status = Column(String(50), index=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    correlation_id = Column(String(36), unique=True, index=True)

    applicant = relationship("ApplicantModel", back_populates="application", uselist=False)
    credit_record = relationship(
        "CreditRecordModel", back_populates="application", uselist=False
    )
    employment_info = relationship(
        "EmploymentInfoModel", back_populates="application", uselist=False
    )
    loan_details = relationship(
        "LoanDetailsModel", back_populates="application", uselist=False
    )
    risk_assessment = relationship(
        "RiskAssessmentModel", back_populates="application", uselist=False
    )
    decision = relationship("LoanDecisionModel", back_populates="application", uselist=False)
    audit_logs = relationship("AuditLogModel", back_populates="application")
    workflow_execution = relationship("WorkflowExecutionModel", back_populates="application", uselist=False)


class ApplicantModel(Base):
    """Applicant profile model."""

    __tablename__ = "applicants"

    id = Column(String(36), primary_key=True, index=True)
    application_id = Column(String(36), ForeignKey("loan_applications.id"))
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100), index=True)
    phone = Column(String(20))
    date_of_birth = Column(String(10))
    ssn = Column(String(11), unique=True, index=True)
    address = Column(String(200))
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(10))

    application = relationship("LoanApplicationModel", back_populates="applicant")


class EmploymentInfoModel(Base):
    """Employment information model."""

    __tablename__ = "employment_info"

    id = Column(String(36), primary_key=True, index=True)
    application_id = Column(String(36), ForeignKey("loan_applications.id"))
    employment_type = Column(String(50))
    employer_name = Column(String(200))
    job_title = Column(String(100))
    years_employed = Column(Float)
    annual_income = Column(Float)
    monthly_income = Column(Float, nullable=True)

    application = relationship("LoanApplicationModel", back_populates="employment_info")


class CreditRecordModel(Base):
    """Credit record model."""

    __tablename__ = "credit_records"

    id = Column(String(36), primary_key=True, index=True)
    application_id = Column(String(36), ForeignKey("loan_applications.id"))
    credit_score = Column(Integer)
    years_of_credit_history = Column(Float)
    number_of_accounts = Column(Integer)
    delinquencies_last_24_months = Column(Integer)
    public_records = Column(Integer)
    current_debt = Column(Float)

    application = relationship("LoanApplicationModel", back_populates="credit_record")


class LoanDetailsModel(Base):
    """Loan details model."""

    __tablename__ = "loan_details"

    id = Column(String(36), primary_key=True, index=True)
    application_id = Column(String(36), ForeignKey("loan_applications.id"))
    loan_amount = Column(Float)
    loan_purpose = Column(String(200))
    loan_term_months = Column(Integer)
    interest_rate = Column(Float, nullable=True)
    additional_notes = Column(Text, nullable=True)

    application = relationship("LoanApplicationModel", back_populates="loan_details")


class RiskAssessmentModel(Base):
    """Risk assessment model."""

    __tablename__ = "risk_assessments"

    id = Column(String(36), primary_key=True, index=True)
    application_id = Column(String(36), ForeignKey("loan_applications.id"))
    debt_to_income_ratio = Column(Float)
    dti_risk_level = Column(String(50))
    credit_score_risk_level = Column(String(50))
    anomalies_detected = Column(JSON, default=[])
    overall_risk_score = Column(Float)
    assessed_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("LoanApplicationModel", back_populates="risk_assessment")


class LoanDecisionModel(Base):
    """Loan decision model."""

    __tablename__ = "loan_decisions"

    id = Column(String(36), primary_key=True, index=True)
    application_id = Column(String(36), ForeignKey("loan_applications.id"))
    classification = Column(String(50), index=True)
    confidence_score = Column(Float)
    risk_factors = Column(JSON, default=[])
    positive_factors = Column(JSON, default=[])
    reasoning = Column(Text)
    recommended_interest_rate = Column(Float, nullable=True)
    conditions = Column(JSON, default=[])
    decided_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("LoanApplicationModel", back_populates="decision")


class AuditLogModel(Base):
    """Audit log model for tracking all actions."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, index=True)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), index=True)
    action = Column(String(100))
    agent_name = Column(String(100), nullable=True)
    details = Column(JSON, default={})
    correlation_id = Column(String(36), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    application = relationship("LoanApplicationModel", back_populates="audit_logs")


class WorkflowExecutionModel(Base):
    """Workflow execution model for tracking orchestration state and progress."""

    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True, index=True)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), unique=True, index=True)
    correlation_id = Column(String(36), index=True)
    workflow_state = Column(String(50), index=True)  # started, in_progress, completed, failed
    current_step = Column(String(50), index=True)  # validate, applicant, risk, decision, complete
    attempt_number = Column(Integer, default=1)

    applicant_result = Column(JSON, nullable=True, default=None)
    risk_result = Column(JSON, nullable=True, default=None)
    decision_result = Column(JSON, nullable=True, default=None)

    error_message = Column(Text, nullable=True)
    error_step = Column(String(50), nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    step_started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    application = relationship("LoanApplicationModel", back_populates="workflow_execution")
