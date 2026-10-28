"""Unit tests for the Financial Risk Analysis Agent."""

import pytest
from datetime import datetime

from agents.risk_agent import FinancialRiskAnalysisAgent
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
    """Create a risk agent instance for testing."""
    return FinancialRiskAnalysisAgent()


@pytest.fixture
def sample_application():
    """Create a sample loan application for testing."""
    return LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="555-1234567",
            date_of_birth="1990-01-01",
            ssn="123-45-6789",
            address="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.FULL_TIME,
            employer_name="Acme Corp",
            job_title="Software Engineer",
            years_employed=5.0,
            annual_income=80000.0,
            monthly_income=6666.67,
        ),
        credit_record=CreditRecord(
            credit_score=750,
            years_of_credit_history=10.0,
            number_of_accounts=5,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=15000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=25000.0,
            loan_purpose="Home improvement",
            loan_term_months=60,
            interest_rate=5.5,
        ),
    )


class TestDTICalculation:
    """Test Debt-to-Income ratio calculation."""

    def test_dti_calculation_normal(self, risk_agent):
        """Test normal DTI calculation."""
        dti = risk_agent.calculate_dti_ratio(annual_income=60000, monthly_debt_obligations=1500)
        assert dti == 30.0  # (1500 / 5000) * 100

    def test_dti_calculation_high(self, risk_agent):
        """Test high DTI calculation."""
        dti = risk_agent.calculate_dti_ratio(annual_income=60000, monthly_debt_obligations=2500)
        assert dti == 50.0  # (2500 / 5000) * 100

    def test_dti_calculation_zero_income(self, risk_agent):
        """Test DTI calculation with zero income."""
        dti = risk_agent.calculate_dti_ratio(annual_income=0, monthly_debt_obligations=1000)
        assert dti == 100.0

    def test_dti_calculation_negative_income(self, risk_agent):
        """Test DTI calculation with negative income."""
        dti = risk_agent.calculate_dti_ratio(annual_income=-50000, monthly_debt_obligations=1000)
        assert dti == 100.0

    def test_dti_calculation_capped(self, risk_agent):
        """Test that DTI is capped at 100%."""
        dti = risk_agent.calculate_dti_ratio(annual_income=10000, monthly_debt_obligations=2000)
        assert dti == 100.0


class TestDTIRiskAssessment:
    """Test DTI risk level assessment."""

    def test_dti_risk_low(self, risk_agent):
        """Test low DTI risk level."""
        risk_level = risk_agent.assess_dti_risk(dti_ratio=30.0)
        assert risk_level == "low"

    def test_dti_risk_medium_lower(self, risk_agent):
        """Test medium DTI risk level (lower bound)."""
        risk_level = risk_agent.assess_dti_risk(dti_ratio=36.0)
        assert risk_level == "medium"

    def test_dti_risk_medium_upper(self, risk_agent):
        """Test medium DTI risk level (upper bound)."""
        risk_level = risk_agent.assess_dti_risk(dti_ratio=43.0)
        assert risk_level == "medium"

    def test_dti_risk_high(self, risk_agent):
        """Test high DTI risk level."""
        risk_level = risk_agent.assess_dti_risk(dti_ratio=50.0)
        assert risk_level == "high"


class TestCreditScoreRiskMapping:
    """Test credit score to risk level mapping."""

    def test_credit_score_excellent(self, risk_agent):
        """Test excellent credit score risk mapping."""
        risk_level, risk_factor = risk_agent.map_credit_score_to_risk(750)
        assert risk_level == "low"
        assert risk_factor == 0.1

    def test_credit_score_good(self, risk_agent):
        """Test good credit score risk mapping."""
        risk_level, risk_factor = risk_agent.map_credit_score_to_risk(710)
        assert risk_level == "low"
        assert risk_factor == 0.2

    def test_credit_score_fair(self, risk_agent):
        """Test fair credit score risk mapping."""
        risk_level, risk_factor = risk_agent.map_credit_score_to_risk(660)
        assert risk_level == "medium"
        assert risk_factor == 0.4

    def test_credit_score_poor(self, risk_agent):
        """Test poor credit score risk mapping."""
        risk_level, risk_factor = risk_agent.map_credit_score_to_risk(600)
        assert risk_level == "medium"
        assert risk_factor == 0.6

    def test_credit_score_very_poor(self, risk_agent):
        """Test very poor credit score risk mapping."""
        risk_level, risk_factor = risk_agent.map_credit_score_to_risk(500)
        assert risk_level == "high"
        assert risk_factor == 1.0


class TestCreditRiskDetails:
    """Test detailed credit risk assessment."""

    def test_no_credit_issues(self, risk_agent):
        """Test applicant with no credit issues."""
        credit_record = CreditRecord(
            credit_score=750,
            years_of_credit_history=10.0,
            number_of_accounts=5,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=10000.0,
        )
        result = risk_agent.assess_credit_risk_details(credit_record)
        assert result["credit_score_risk_level"] == "low"
        assert len(result["risk_factors"]) == 0
        assert result["risk_contribution"] == 0.0

    def test_delinquencies_detected(self, risk_agent):
        """Test detection of delinquencies."""
        credit_record = CreditRecord(
            credit_score=650,
            years_of_credit_history=5.0,
            number_of_accounts=3,
            delinquencies_last_24_months=2,
            public_records=0,
            current_debt=20000.0,
        )
        result = risk_agent.assess_credit_risk_details(credit_record)
        assert len(result["risk_factors"]) > 0
        assert any("delinquencies" in factor.lower() for factor in result["risk_factors"])

    def test_public_records_detected(self, risk_agent):
        """Test detection of public records."""
        credit_record = CreditRecord(
            credit_score=600,
            years_of_credit_history=3.0,
            number_of_accounts=2,
            delinquencies_last_24_months=0,
            public_records=1,
            current_debt=15000.0,
        )
        result = risk_agent.assess_credit_risk_details(credit_record)
        assert any("public records" in factor.lower() for factor in result["risk_factors"])

    def test_limited_credit_history(self, risk_agent):
        """Test detection of limited credit history."""
        credit_record = CreditRecord(
            credit_score=680,
            years_of_credit_history=1.5,
            number_of_accounts=2,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=5000.0,
        )
        result = risk_agent.assess_credit_risk_details(credit_record)
        assert any("credit history" in factor.lower() for factor in result["risk_factors"])


class TestLoanAmountRisk:
    """Test loan amount risk assessment."""

    def test_reasonable_loan_amount(self, risk_agent):
        """Test reasonable loan amount risk."""
        risk_level, risk_score, factors = risk_agent.assess_loan_amount_risk(
            loan_amount=25000.0, annual_income=80000.0, current_debt=15000.0, loan_term_months=60
        )
        assert risk_level == "low"
        assert risk_score < 0.2
        assert len(factors) == 0

    def test_high_loan_to_income(self, risk_agent):
        """Test high loan-to-income ratio."""
        risk_level, risk_score, factors = risk_agent.assess_loan_amount_risk(
            loan_amount=500000.0, annual_income=60000.0, current_debt=50000.0, loan_term_months=360
        )
        assert risk_level == "high"
        assert risk_score > 0.3
        assert any("Loan-to-Income" in factor for factor in factors)

    def test_short_loan_term(self, risk_agent):
        """Test short loan term risk."""
        risk_level, risk_score, factors = risk_agent.assess_loan_amount_risk(
            loan_amount=50000.0, annual_income=80000.0, current_debt=20000.0, loan_term_months=6
        )
        assert any("loan term" in factor.lower() for factor in factors)


class TestAnomalyDetection:
    """Test anomaly detection."""

    def test_no_anomalies(self, risk_agent):
        """Test application with no anomalies."""
        app_data = {
            "employment_info": {
                "annual_income": 80000.0,
                "monthly_income": 6666.67,
                "years_employed": 5.0,
            },
            "credit_record": {
                "current_debt": 15000.0,
                "delinquencies_last_24_months": 0,
            },
            "loan_details": {
                "loan_amount": 25000.0,
                "loan_purpose": "Home improvement",
                "loan_term_months": 60,
            },
            "applicant_profile": {},
        }
        anomalies = risk_agent.detect_anomalies(app_data)
        assert len(anomalies) == 0

    def test_income_mismatch_detected(self, risk_agent):
        """Test detection of income mismatch."""
        app_data = {
            "employment_info": {
                "annual_income": 80000.0,
                "monthly_income": 3000.0,  # Should be ~6667
                "years_employed": 5.0,
            },
            "credit_record": {
                "current_debt": 15000.0,
                "delinquencies_last_24_months": 0,
            },
            "loan_details": {
                "loan_amount": 25000.0,
                "loan_purpose": "Home improvement",
                "loan_term_months": 60,
            },
            "applicant_profile": {},
        }
        anomalies = risk_agent.detect_anomalies(app_data)
        assert any("income" in anomaly.lower() for anomaly in anomalies)

    def test_recent_employment_detected(self, risk_agent):
        """Test detection of recent employment change."""
        app_data = {
            "employment_info": {
                "annual_income": 80000.0,
                "monthly_income": 6666.67,
                "years_employed": 0.3,  # Less than 6 months
            },
            "credit_record": {
                "current_debt": 15000.0,
                "delinquencies_last_24_months": 0,
            },
            "loan_details": {
                "loan_amount": 25000.0,
                "loan_purpose": "Home improvement",
                "loan_term_months": 60,
            },
            "applicant_profile": {},
        }
        anomalies = risk_agent.detect_anomalies(app_data)
        assert any("employment" in anomaly.lower() for anomaly in anomalies)

    def test_multiple_delinquencies_detected(self, risk_agent):
        """Test detection of multiple recent delinquencies."""
        app_data = {
            "employment_info": {
                "annual_income": 80000.0,
                "monthly_income": 6666.67,
                "years_employed": 5.0,
            },
            "credit_record": {
                "current_debt": 15000.0,
                "delinquencies_last_24_months": 5,
            },
            "loan_details": {
                "loan_amount": 25000.0,
                "loan_purpose": "Home improvement",
                "loan_term_months": 60,
            },
            "applicant_profile": {},
        }
        anomalies = risk_agent.detect_anomalies(app_data)
        assert any("delinquencies" in anomaly.lower() for anomaly in anomalies)


class TestOverallRiskScore:
    """Test overall risk score calculation."""

    def test_low_risk_score(self, risk_agent):
        """Test calculation of low risk score."""
        score = risk_agent.calculate_overall_risk_score(
            dti_risk_level="low",
            credit_risk_level="low",
            loan_amount_risk_level="low",
            credit_risk_contribution=0.1,
            loan_amount_risk_contribution=0.1,
            anomalies_count=0,
        )
        assert 0 <= score <= 30

    def test_medium_risk_score(self, risk_agent):
        """Test calculation of medium risk score."""
        score = risk_agent.calculate_overall_risk_score(
            dti_risk_level="medium",
            credit_risk_level="medium",
            loan_amount_risk_level="medium",
            credit_risk_contribution=0.5,
            loan_amount_risk_contribution=0.5,
            anomalies_count=1,
        )
        assert 30 <= score <= 70

    def test_high_risk_score(self, risk_agent):
        """Test calculation of high risk score."""
        score = risk_agent.calculate_overall_risk_score(
            dti_risk_level="high",
            credit_risk_level="high",
            loan_amount_risk_level="high",
            credit_risk_contribution=1.0,
            loan_amount_risk_contribution=1.0,
            anomalies_count=5,
        )
        assert score >= 70

    def test_risk_score_range(self, risk_agent):
        """Test that risk score is always in valid range."""
        score = risk_agent.calculate_overall_risk_score(
            dti_risk_level="high",
            credit_risk_level="high",
            loan_amount_risk_level="high",
            credit_risk_contribution=2.0,  # Artificially high
            loan_amount_risk_contribution=2.0,
            anomalies_count=100,
        )
        assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_analyze_integration(risk_agent, sample_application):
    """Test complete risk analysis integration."""
    result = await risk_agent.analyze(sample_application)

    # Verify result structure
    assert "risk_score" in result
    assert "dti_ratio" in result
    assert "dti_risk_level" in result
    assert "credit_risk" in result
    assert "loan_amount_risk" in result
    assert "anomalies" in result
    assert "risk_factors" in result
    assert "positive_factors" in result
    assert "analyzed_at" in result

    # Verify value ranges
    assert 0 <= result["risk_score"] <= 100
    assert result["dti_risk_level"] in ["low", "medium", "high"]
    assert result["credit_risk"] in ["low", "medium", "high"]
    assert result["loan_amount_risk"] in ["low", "medium", "high"]

    # Verify positive factors for good profile
    assert len(result["positive_factors"]) > 0
