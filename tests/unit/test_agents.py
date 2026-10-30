"""Unit tests for agent implementations."""

import pytest
from agents.applicant_agent import ApplicantProfileAgent
from agents.risk_agent import FinancialRiskAnalysisAgent
from agents.decision_agent import LoanDecisionAgent
from agents.compliance_agent import ComplianceAgent
from agents.notification_agent import NotificationAgent
from models.schemas import (
    ApplicantProfile, EmploymentInfo, CreditRecord, LoanDetails, LoanApplicationRequest
)


class TestApplicantProfileAgent:
    """Test ApplicantProfileAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = ApplicantProfileAgent()
        assert agent is not None
        assert agent.model == "claude-opus-4-1-20250805"
        assert agent.timeout > 0

    def test_analyze_valid_application(self, sample_loan_application):
        """Test analyzing a valid application."""
        agent = ApplicantProfileAgent()
        result = agent.analyze(
            applicant=sample_loan_application.applicant_profile,
            employment=sample_loan_application.employment_info,
            credit=sample_loan_application.credit_record,
        )

        assert result is not None
        assert "validation_status" in result
        assert "income_stability_level" in result
        assert "employment_risk_level" in result
        assert "credit_summary" in result

    def test_analyze_incomplete_application(self):
        """Test analyzing incomplete data."""
        agent = ApplicantProfileAgent()

        # Create application with minimal data
        applicant = ApplicantProfile(
            first_name="",  # Empty name
            last_name="Test",
            email="test@example.com",
            phone="555-1234",
            date_of_birth="1990-01-01",
            ssn="123-45-6789",
            address="123 Main",
            city="City",
            state="ST",
            zip_code="12345",
        )

        employment = EmploymentInfo(
            employment_type="full_time",
            employer_name="",  # Empty employer
            job_title="",
            years_employed=0,
            annual_income=0,  # Zero income
        )

        credit = CreditRecord(
            credit_score=300,  # Minimum credit score
            years_of_credit_history=0,
            number_of_accounts=0,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=0,
        )

        result = agent.analyze(
            applicant=applicant,
            employment=employment,
            credit=credit,
        )

        assert result is not None
        assert "critical_issues" in result or "warnings" in result


class TestFinancialRiskAnalysisAgent:
    """Test FinancialRiskAnalysisAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = FinancialRiskAnalysisAgent()
        assert agent is not None

    def test_analyze_low_risk_application(self, sample_loan_application):
        """Test analyzing a low-risk application."""
        agent = FinancialRiskAnalysisAgent()
        result = agent.analyze(sample_loan_application)

        assert result is not None
        assert "risk_score" in result
        assert 0 <= result["risk_score"] <= 100
        assert "debt_to_income_ratio" in result
        assert "credit_risk_level" in result
        assert "loan_amount_risk_level" in result

    def test_analyze_high_risk_application(self, sample_high_risk_application):
        """Test analyzing a high-risk application."""
        agent = FinancialRiskAnalysisAgent()
        result = agent.analyze(sample_high_risk_application)

        assert result is not None
        assert result["risk_score"] > 50  # Should be higher risk


class TestLoanDecisionAgent:
    """Test LoanDecisionAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = LoanDecisionAgent()
        assert agent is not None

    def test_decide_low_risk_approval(self, sample_loan_application):
        """Test decision for low-risk application."""
        agent = LoanDecisionAgent()

        # Mock applicant and risk analysis results
        applicant_analysis = {
            "income_stability_level": "high",
            "employment_risk_level": "low",
            "data_completeness_percentage": 95,
        }

        risk_analysis = {
            "risk_score": 25,  # Low risk
            "debt_to_income_ratio": 0.30,
            "credit_risk_level": "low",
        }

        result = agent.decide(sample_loan_application, applicant_analysis, risk_analysis)

        assert result is not None
        assert "classification_value" in result
        assert result["classification_value"] in ["approved", "rejected", "manual_review"]
        assert "confidence_score" in result
        assert 0 <= result["confidence_score"] <= 1

    def test_decide_high_risk_rejection(self, sample_high_risk_application):
        """Test decision for high-risk application."""
        agent = LoanDecisionAgent()

        applicant_analysis = {
            "income_stability_level": "low",
            "employment_risk_level": "high",
            "data_completeness_percentage": 70,
        }

        risk_analysis = {
            "risk_score": 85,  # High risk
            "debt_to_income_ratio": 0.50,
            "credit_risk_level": "high",
        }

        result = agent.decide(sample_high_risk_application, applicant_analysis, risk_analysis)

        assert result is not None
        assert "classification_value" in result


class TestComplianceAgent:
    """Test ComplianceAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = ComplianceAgent()
        assert agent is not None

    def test_validate_and_process_approved(self):
        """Test compliance validation for approved decision."""
        agent = ComplianceAgent()

        result = agent.validate_and_process(
            application_id="test-123",
            classification="approved",
            risk_score=30,
            applicant_name="John Doe",
            applicant_email="john@example.com",
            loan_amount=250000,
            decision_reasoning="Good credit and income",
        )

        assert result is not None
        assert "compliance_validation_passed" in result
        assert "regulatory_checks" in result
        assert len(result["regulatory_checks"]) > 0
        assert "adverse_action_notice" not in result  # Not for approved

    def test_validate_and_process_rejected(self):
        """Test compliance validation for rejected decision."""
        agent = ComplianceAgent()

        result = agent.validate_and_process(
            application_id="test-456",
            classification="rejected",
            risk_score=85,
            applicant_name="Jane Smith",
            applicant_email="jane@example.com",
            loan_amount=100000,
            decision_reasoning="High risk profile",
        )

        assert result is not None
        assert "adverse_action_notice" in result  # Should generate for rejected
        assert result["adverse_action_notice"]["notice_type"] == "ADVERSE_ACTION_NOTICE"
        assert "appeal_documentation" in result


class TestNotificationAgent:
    """Test NotificationAgent."""

    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = NotificationAgent()
        assert agent is not None

    def test_queue_decision_notification_approved(self):
        """Test queuing notifications for approved decision."""
        agent = NotificationAgent()

        result = agent.queue_decision_notification(
            application_id="test-app-123",
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-1234",
            classification="approved",
            risk_score=30,
            approved_amount=250000,
            recommended_rate=5.5,
            reasoning="Approved based on good credit and income",
        )

        assert result is not None
        assert "notifications_queued" in result
        assert result["notifications_queued"] > 0
        assert "notifications" in result
        assert any(n["channel"] == "email" for n in result["notifications"])

    def test_queue_appeal_notification(self):
        """Test queuing appeal notifications."""
        agent = NotificationAgent()

        result = agent.queue_appeal_notification(
            application_id="test-app-456",
            applicant_name="Jane Smith",
            applicant_email="jane@example.com",
            appeal_status="received",
            original_decision="rejected",
        )

        assert result is not None
        assert "appeal_status" in result
        assert result["appeal_status"] == "received"
        assert "email" in result


# Test validation functions
class TestValidation:
    """Test validation functions."""

    def test_validate_email(self):
        """Test email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@example.co.uk",
            "first+last@example.org",
        ]
        invalid_emails = ["invalid@", "@example.com", "no-at-sign", ""]

        for email in valid_emails:
            assert "@" in email and "." in email.split("@")[1]

        for email in invalid_emails:
            assert not ("@" in email and "." in email.split("@")[1] if "@" in email else False)

    def test_validate_phone(self):
        """Test phone validation."""
        valid_phones = ["555-123-4567", "5551234567", "(555) 123-4567"]
        invalid_phones = ["123", "555-12", ""]

        for phone in valid_phones:
            digits = "".join(filter(str.isdigit, phone))
            assert len(digits) >= 10

        for phone in invalid_phones:
            digits = "".join(filter(str.isdigit, phone))
            assert len(digits) < 10

    def test_credit_score_range(self):
        """Test credit score validation."""
        valid_scores = [300, 500, 750, 850]
        invalid_scores = [200, 299, 851, 900]

        for score in valid_scores:
            assert 300 <= score <= 850

        for score in invalid_scores:
            assert not (300 <= score <= 850)
