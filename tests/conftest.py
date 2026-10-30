"""Pytest configuration and fixtures."""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Create all tables
    from database.db import Base
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_session(test_engine):
    """Create a new database session for each test."""
    Session = sessionmaker(bind=test_engine)
    session = Session()

    yield session

    session.rollback()
    session.close()


@pytest.fixture
def sample_loan_application():
    """Create a sample loan application for testing."""
    from models.schemas import LoanApplicationRequest, ApplicantProfile, EmploymentInfo, CreditRecord, LoanDetails

    return LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="555-123-4567",
            date_of_birth="1990-01-15",
            ssn="123-45-6789",
            address="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
        ),
        employment_info=EmploymentInfo(
            employment_type="full_time",
            employer_name="Acme Corp",
            job_title="Software Engineer",
            years_employed=5.0,
            annual_income=120000.0,
            monthly_income=10000.0,
        ),
        credit_record=CreditRecord(
            credit_score=750,
            years_of_credit_history=15.0,
            number_of_accounts=8,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=50000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=250000.0,
            loan_purpose="Home",
            loan_term_months=360,
            interest_rate=5.5,
        ),
        additional_notes="Good credit history",
    )


@pytest.fixture
def sample_high_risk_application():
    """Create a high-risk sample application for testing."""
    from models.schemas import LoanApplicationRequest, ApplicantProfile, EmploymentInfo, CreditRecord, LoanDetails

    return LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="555-987-6543",
            date_of_birth="1985-06-20",
            ssn="987-65-4321",
            address="456 Oak Ave",
            city="Chicago",
            state="IL",
            zip_code="60601",
        ),
        employment_info=EmploymentInfo(
            employment_type="self_employed",
            employer_name="Smith Consulting",
            job_title="Consultant",
            years_employed=2.0,
            annual_income=60000.0,
        ),
        credit_record=CreditRecord(
            credit_score=580,
            years_of_credit_history=5.0,
            number_of_accounts=3,
            delinquencies_last_24_months=2,
            public_records=1,
            current_debt=25000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=100000.0,
            loan_purpose="Debt Consolidation",
            loan_term_months=120,
        ),
        additional_notes="Previous financial difficulties",
    )


@pytest.fixture
def mock_claude_response():
    """Create a mock Claude API response."""
    return {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "This is a mock Claude response for testing purposes.",
            }
        ],
        "model": "claude-opus-4-1-20250805",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 20},
    }
