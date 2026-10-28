"""Integration tests for the Financial Risk Analysis Agent."""

import pytest
import asyncio
from datetime import datetime

from agents.risk_agent import get_risk_agent, FinancialRiskAnalysisAgent
from models.schemas import (
    ApplicantProfile,
    EmploymentInfo,
    CreditRecord,
    LoanDetails,
    LoanApplicationRequest,
    EmploymentType,
)


@pytest.fixture
def risk_agent():
    """Get the risk analysis agent."""
    return get_risk_agent()


@pytest.fixture
def good_applicant():
    """Create a loan application for an applicant with good profile."""
    return LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="555-9876543",
            date_of_birth="1985-05-15",
            ssn="987-65-4321",
            address="456 Oak Ave",
            city="Springfield",
            state="IL",
            zip_code="62702",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.FULL_TIME,
            employer_name="Tech Solutions Inc",
            job_title="Senior Developer",
            years_employed=7.0,
            annual_income=120000.0,
            monthly_income=10000.0,
        ),
        credit_record=CreditRecord(
            credit_score=780,
            years_of_credit_history=15.0,
            number_of_accounts=8,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=12000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=30000.0,
            loan_purpose="Business expansion",
            loan_term_months=72,
            interest_rate=4.5,
        ),
    )


@pytest.fixture
def risky_applicant():
    """Create a loan application for an applicant with risky profile."""
    return LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="Bob",
            last_name="Johnson",
            email="bob@example.com",
            phone="555-5555555",
            date_of_birth="1992-03-20",
            ssn="555-55-5555",
            address="789 Pine Ln",
            city="Shelbyville",
            state="IL",
            zip_code="62702",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.SELF_EMPLOYED,
            employer_name="Self Employed",
            job_title="Contractor",
            years_employed=1.5,
            annual_income=45000.0,
            monthly_income=3750.0,
        ),
        credit_record=CreditRecord(
            credit_score=580,
            years_of_credit_history=4.0,
            number_of_accounts=3,
            delinquencies_last_24_months=2,
            public_records=1,
            current_debt=35000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=250000.0,
            loan_purpose="Debt consolidation",
            loan_term_months=120,
            interest_rate=12.0,
        ),
    )


@pytest.fixture
def moderate_applicant():
    """Create a loan application for an applicant with moderate profile."""
    return LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="Alice",
            last_name="Williams",
            email="alice@example.com",
            phone="555-1111111",
            date_of_birth="1988-07-10",
            ssn="111-11-1111",
            address="321 Elm St",
            city="Capital City",
            state="IL",
            zip_code="62701",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.FULL_TIME,
            employer_name="Manufacturing Corp",
            job_title="Plant Manager",
            years_employed=3.5,
            annual_income=65000.0,
            monthly_income=5416.67,
        ),
        credit_record=CreditRecord(
            credit_score=680,
            years_of_credit_history=7.0,
            number_of_accounts=4,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=20000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=35000.0,
            loan_purpose="Vehicle purchase",
            loan_term_months=60,
            interest_rate=6.5,
        ),
    )


class TestRiskAnalysisComparison:
    """Test risk analysis across different applicant profiles."""

    @pytest.mark.asyncio
    async def test_good_applicant_low_risk(self, risk_agent, good_applicant):
        """Test that good applicant receives low risk score."""
        result = await risk_agent.analyze(good_applicant)

        assert result["risk_score"] < 40
        assert result["dti_risk_level"] in ["low", "medium"]
        assert result["credit_risk"] == "low"
        assert len(result["positive_factors"]) > 0
        assert len(result["anomalies"]) == 0

    @pytest.mark.asyncio
    async def test_risky_applicant_high_risk(self, risk_agent, risky_applicant):
        """Test that risky applicant receives high risk score."""
        result = await risk_agent.analyze(risky_applicant)

        assert result["risk_score"] >= 60
        assert result["dti_risk_level"] == "high"
        assert result["credit_risk"] == "high"
        assert len(result["risk_factors"]) > 0

    @pytest.mark.asyncio
    async def test_moderate_applicant_medium_risk(
        self, risk_agent, moderate_applicant
    ):
        """Test that moderate applicant receives medium risk score."""
        result = await risk_agent.analyze(moderate_applicant)

        assert 30 <= result["risk_score"] <= 70
        assert result["credit_risk"] in ["low", "medium"]
        assert len(result["risk_factors"]) >= 0


class TestRiskAnalysisOutput:
    """Test structure and content of risk analysis output."""

    @pytest.mark.asyncio
    async def test_analysis_output_structure(self, risk_agent, good_applicant):
        """Verify risk analysis output has all required fields."""
        result = await risk_agent.analyze(good_applicant)

        # Required fields
        required_fields = [
            "risk_score",
            "dti_ratio",
            "dti_risk_level",
            "credit_risk",
            "credit_score_value",
            "loan_amount_risk",
            "anomalies",
            "risk_factors",
            "positive_factors",
            "analyzed_at",
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    @pytest.mark.asyncio
    async def test_risk_factors_not_empty_for_risky_applicant(
        self, risk_agent, risky_applicant
    ):
        """Verify risk factors are populated for risky applicants."""
        result = await risk_agent.analyze(risky_applicant)

        assert len(result["risk_factors"]) > 0
        assert all(isinstance(factor, str) for factor in result["risk_factors"])

    @pytest.mark.asyncio
    async def test_positive_factors_for_good_applicant(
        self, risk_agent, good_applicant
    ):
        """Verify positive factors are identified for good applicants."""
        result = await risk_agent.analyze(good_applicant)

        assert len(result["positive_factors"]) > 0
        assert all(isinstance(factor, str) for factor in result["positive_factors"])


class TestRiskCalculationConsistency:
    """Test consistency of risk calculations."""

    @pytest.mark.asyncio
    async def test_same_data_same_score(self, risk_agent, good_applicant):
        """Test that same data produces same risk score."""
        result1 = await risk_agent.analyze(good_applicant)
        result2 = await risk_agent.analyze(good_applicant)

        assert result1["risk_score"] == result2["risk_score"]
        assert result1["dti_ratio"] == result2["dti_ratio"]
        assert result1["credit_risk"] == result2["credit_risk"]

    @pytest.mark.asyncio
    async def test_dti_calculation_consistency(self, risk_agent):
        """Test DTI calculation is consistent."""
        dti1 = risk_agent.calculate_dti_ratio(
            annual_income=80000, monthly_debt_obligations=2000
        )
        dti2 = risk_agent.calculate_dti_ratio(
            annual_income=80000, monthly_debt_obligations=2000
        )

        assert dti1 == dti2


class TestRiskEdgeCases:
    """Test edge cases in risk analysis."""

    @pytest.mark.asyncio
    async def test_very_high_income_low_loan(self, risk_agent):
        """Test applicant with very high income and low loan amount."""
        app = LoanApplicationRequest(
            applicant_profile=ApplicantProfile(
                first_name="Rich",
                last_name="Guy",
                email="rich@example.com",
                phone="555-9999999",
                date_of_birth="1980-01-01",
                ssn="999-99-9999",
                address="Mansion Lane",
                city="Springfield",
                state="IL",
                zip_code="62701",
            ),
            employment_info=EmploymentInfo(
                employment_type=EmploymentType.FULL_TIME,
                employer_name="Fortune 500",
                job_title="Executive",
                years_employed=20.0,
                annual_income=500000.0,
                monthly_income=41666.67,
            ),
            credit_record=CreditRecord(
                credit_score=800,
                years_of_credit_history=25.0,
                number_of_accounts=10,
                delinquencies_last_24_months=0,
                public_records=0,
                current_debt=50000.0,
            ),
            loan_details=LoanDetails(
                loan_amount=10000.0,
                loan_purpose="Personal loan",
                loan_term_months=24,
                interest_rate=3.0,
            ),
        )

        result = await risk_agent.analyze(app)

        assert result["risk_score"] < 20
        assert result["dti_risk_level"] == "low"

    @pytest.mark.asyncio
    async def test_minimal_income_large_loan(self, risk_agent):
        """Test applicant with minimal income requesting large loan."""
        app = LoanApplicationRequest(
            applicant_profile=ApplicantProfile(
                first_name="Poor",
                last_name="Guy",
                email="poor@example.com",
                phone="555-0000000",
                date_of_birth="1995-01-01",
                ssn="000-00-0000",
                address="Small House",
                city="Springfield",
                state="IL",
                zip_code="62701",
            ),
            employment_info=EmploymentInfo(
                employment_type=EmploymentType.PART_TIME,
                employer_name="Local Store",
                job_title="Clerk",
                years_employed=0.5,
                annual_income=15000.0,
                monthly_income=1250.0,
            ),
            credit_record=CreditRecord(
                credit_score=500,
                years_of_credit_history=1.0,
                number_of_accounts=1,
                delinquencies_last_24_months=1,
                public_records=0,
                current_debt=5000.0,
            ),
            loan_details=LoanDetails(
                loan_amount=100000.0,
                loan_purpose="Home purchase",
                loan_term_months=360,
                interest_rate=8.0,
            ),
        )

        result = await risk_agent.analyze(app)

        assert result["risk_score"] > 80
        assert result["dti_risk_level"] == "high"
        assert len(result["anomalies"]) > 0


class TestRiskAgentSingleton:
    """Test risk agent singleton pattern."""

    def test_agent_singleton(self):
        """Test that get_risk_agent returns same instance."""
        agent1 = get_risk_agent()
        agent2 = get_risk_agent()

        assert agent1 is agent2


class TestRiskAnalysisPerformance:
    """Test performance characteristics of risk analysis."""

    @pytest.mark.asyncio
    async def test_analysis_completes_quickly(self, risk_agent, good_applicant):
        """Test that risk analysis completes in reasonable time."""
        import time

        start_time = time.time()
        result = await risk_agent.analyze(good_applicant)
        elapsed_time = time.time() - start_time

        # Should complete in less than 10 seconds
        assert elapsed_time < 10.0
        assert "risk_score" in result
