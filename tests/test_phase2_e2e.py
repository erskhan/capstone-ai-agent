"""End-to-end tests for Phase 2: Core Agent Development."""

import pytest
from datetime import datetime
from uuid import uuid4

from models.schemas import (
    ApplicantProfile,
    EmploymentInfo,
    EmploymentType,
    CreditRecord,
    LoanDetails,
    LoanApplicationRequest,
    DecisionClassification,
)
from agents.applicant_agent import ApplicantProfileAgent
from agents.risk_agent import FinancialRiskAnalysisAgent
from agents.decision_agent import LoanDecisionAgent
from agents.orchestrator import LoanApprovalOrchestrator


@pytest.fixture
def good_applicant_application():
    """Create a sample good-profile loan application."""
    return LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="5551234567",
            date_of_birth="1985-06-15",
            ssn="123456789",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            zip_code="94102",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.FULL_TIME,
            employer_name="Tech Corp",
            job_title="Senior Engineer",
            years_employed=5.5,
            annual_income=150000.0,
            monthly_income=12500.0,
        ),
        credit_record=CreditRecord(
            credit_score=750,
            years_of_credit_history=12.0,
            number_of_accounts=5,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=25000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=50000.0,
            loan_purpose="Home Improvement",
            loan_term_months=60,
            interest_rate=5.5,
        ),
        additional_notes="Excellent credit profile with stable employment",
    )


@pytest.fixture
def risky_applicant_application():
    """Create a sample risky-profile loan application."""
    return LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="5559876543",
            date_of_birth="1988-03-20",
            ssn="987654321",
            address="456 Oak Ave",
            city="Los Angeles",
            state="CA",
            zip_code="90001",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.SELF_EMPLOYED,
            employer_name="Self Employed LLC",
            job_title="Consultant",
            years_employed=1.5,
            annual_income=60000.0,
            monthly_income=5000.0,
        ),
        credit_record=CreditRecord(
            credit_score=580,
            years_of_credit_history=3.0,
            number_of_accounts=2,
            delinquencies_last_24_months=2,
            public_records=1,
            current_debt=45000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=75000.0,
            loan_purpose="Debt Consolidation",
            loan_term_months=72,
            interest_rate=12.5,
        ),
        additional_notes="Recent employment change, some delinquencies",
    )


class TestApplicantProfileAgent:
    """Tests for ApplicantProfileAgent."""

    def test_agent_initialization(self):
        """Test that agent can be initialized."""
        agent = ApplicantProfileAgent()
        assert agent is not None
        assert agent.model == "claude-opus-4-1-20250805"
        assert agent.timeout == 30

    def test_analyze_good_applicant(self, good_applicant_application):
        """Test analysis of a good applicant profile."""
        agent = ApplicantProfileAgent()
        result = agent.analyze(
            applicant=good_applicant_application.applicant_profile,
            employment=good_applicant_application.employment_info,
            credit=good_applicant_application.credit_record,
        )

        assert result is not None
        assert "validation_status" in result
        assert "income_stability_score" in result
        assert "employment_risk_score" in result
        assert "credit_summary" in result
        assert "reasoning" in result

        # Good applicant should have high income stability
        assert result["income_stability_score"] > 60

    def test_analyze_risky_applicant(self, risky_applicant_application):
        """Test analysis of a risky applicant profile."""
        agent = ApplicantProfileAgent()
        result = agent.analyze(
            applicant=risky_applicant_application.applicant_profile,
            employment=risky_applicant_application.employment_info,
            credit=risky_applicant_application.credit_record,
        )

        assert result is not None
        assert "validation_status" in result
        assert "employment_risk_score" in result

        # Risky applicant should have higher employment risk
        assert result["employment_risk_score"] > 50


class TestFinancialRiskAnalysisAgent:
    """Tests for FinancialRiskAnalysisAgent."""

    def test_agent_initialization(self):
        """Test that agent can be initialized."""
        agent = FinancialRiskAnalysisAgent()
        assert agent is not None
        assert agent.model == "claude-opus-4-1-20250805"

    def test_dti_calculation(self):
        """Test DTI ratio calculation."""
        agent = FinancialRiskAnalysisAgent()
        dti = agent.calculate_dti_ratio(annual_income=100000, monthly_debt_obligations=2000)
        assert 0 <= dti <= 100
        assert dti == 24.0  # 2000 / (100000/12) = 24%

    def test_analyze_good_application(self, good_applicant_application):
        """Test risk analysis of a good application."""
        agent = FinancialRiskAnalysisAgent()
        result = agent.analyze(good_applicant_application)

        assert result is not None
        assert "risk_score" in result
        assert "dti_ratio" in result
        assert "credit_risk" in result
        assert "loan_amount_risk" in result

        # Good application should have low risk
        assert result["risk_score"] < 50

    def test_analyze_risky_application(self, risky_applicant_application):
        """Test risk analysis of a risky application."""
        agent = FinancialRiskAnalysisAgent()
        result = agent.analyze(risky_applicant_application)

        assert result is not None
        assert result["risk_score"] > 50


class TestLoanDecisionAgent:
    """Tests for LoanDecisionAgent."""

    def test_agent_initialization(self):
        """Test that agent can be initialized."""
        agent = LoanDecisionAgent()
        assert agent is not None
        assert agent.RISK_THRESHOLD_APPROVE == 35
        assert agent.RISK_THRESHOLD_REVIEW == 65

    def test_classify_by_risk(self):
        """Test decision classification based on risk score."""
        agent = LoanDecisionAgent()

        # Low risk
        classification = agent._classify_by_risk(20)
        assert classification == DecisionClassification.APPROVED

        # Medium risk
        classification = agent._classify_by_risk(50)
        assert classification == DecisionClassification.MANUAL_REVIEW

        # High risk
        classification = agent._classify_by_risk(80)
        assert classification == DecisionClassification.REJECTED

    def test_decide_good_applicant(self, good_applicant_application):
        """Test decision for good applicant."""
        applicant_agent = ApplicantProfileAgent()
        risk_agent = FinancialRiskAnalysisAgent()
        decision_agent = LoanDecisionAgent()

        applicant_analysis = applicant_agent.analyze(
            applicant=good_applicant_application.applicant_profile,
            employment=good_applicant_application.employment_info,
            credit=good_applicant_application.credit_record,
        )

        risk_analysis = risk_agent.analyze(good_applicant_application)

        decision = decision_agent.decide(
            application=good_applicant_application,
            applicant_analysis=applicant_analysis,
            risk_analysis=risk_analysis,
        )

        assert decision is not None
        assert "classification" in decision
        assert "confidence_score" in decision
        assert "reasoning" in decision
        assert decision["classification"] in [
            DecisionClassification.APPROVED,
            DecisionClassification.MANUAL_REVIEW,
        ]


class TestLoanApprovalOrchestrator:
    """Tests for LoanApprovalOrchestrator workflow."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = LoanApprovalOrchestrator()
        assert orchestrator is not None
        assert orchestrator.applicant_agent is not None
        assert orchestrator.risk_agent is not None
        assert orchestrator.decision_agent is not None

    def test_end_to_end_good_applicant(self, good_applicant_application):
        """Test complete workflow for good applicant."""
        orchestrator = LoanApprovalOrchestrator()
        application_id = str(uuid4())
        correlation_id = str(uuid4())

        result = orchestrator.process_application(
            application=good_applicant_application,
            application_id=application_id,
            correlation_id=correlation_id,
        )

        assert result is not None
        assert result["application_id"] == application_id
        assert result["correlation_id"] == correlation_id
        assert result["workflow_state"] == "completed"
        assert "applicant_analysis" in result
        assert "risk_analysis" in result
        assert "decision" in result

        decision = result["decision"]
        assert "classification" in decision
        assert "confidence_score" in decision
        assert "reasoning" in decision

    def test_end_to_end_risky_applicant(self, risky_applicant_application):
        """Test complete workflow for risky applicant."""
        orchestrator = LoanApprovalOrchestrator()
        application_id = str(uuid4())
        correlation_id = str(uuid4())

        result = orchestrator.process_application(
            application=risky_applicant_application,
            application_id=application_id,
            correlation_id=correlation_id,
        )

        assert result is not None
        assert result["workflow_state"] == "completed"
        assert "decision" in result

    def test_workflow_step_tracking(self, good_applicant_application):
        """Test that workflow steps are properly tracked."""
        orchestrator = LoanApprovalOrchestrator()
        application_id = str(uuid4())
        correlation_id = str(uuid4())

        result = orchestrator.process_application(
            application=good_applicant_application,
            application_id=application_id,
            correlation_id=correlation_id,
        )

        assert "steps" in result
        steps = result["steps"]
        assert len(steps) == 4  # validate, applicant, risk, decision

        step_names = [step["name"] for step in steps]
        assert "validate_input" in step_names
        assert "analyze_applicant_profile" in step_names
        assert "analyze_financial_risk" in step_names
        assert "synthesize_decision" in step_names

        # All steps should be completed
        for step in steps:
            assert step["status"] == "completed"
            assert step["error"] is None

    def test_workflow_timing(self, good_applicant_application):
        """Test that workflow timing is recorded."""
        orchestrator = LoanApprovalOrchestrator()
        application_id = str(uuid4())
        correlation_id = str(uuid4())

        result = orchestrator.process_application(
            application=good_applicant_application,
            application_id=application_id,
            correlation_id=correlation_id,
        )

        assert "steps" in result
        for step in result["steps"]:
            if step["status"] == "completed":
                assert step["started_at"] is not None
                assert step["completed_at"] is not None


class TestPhase2Integration:
    """Integration tests for Phase 2 components."""

    def test_agents_work_together(self, good_applicant_application):
        """Test that all three agents work together in workflow."""
        applicant_agent = ApplicantProfileAgent()
        risk_agent = FinancialRiskAnalysisAgent()
        decision_agent = LoanDecisionAgent()

        # Step 1: Analyze applicant
        applicant_result = applicant_agent.analyze(
            applicant=good_applicant_application.applicant_profile,
            employment=good_applicant_application.employment_info,
            credit=good_applicant_application.credit_record,
        )
        assert applicant_result["validation_status"] in ["valid", "incomplete"]

        # Step 2: Analyze risk
        risk_result = risk_agent.analyze(good_applicant_application)
        assert 0 <= risk_result["risk_score"] <= 100

        # Step 3: Make decision
        decision = decision_agent.decide(
            application=good_applicant_application,
            applicant_analysis=applicant_result,
            risk_analysis=risk_result,
        )
        assert decision["classification"] in [
            DecisionClassification.APPROVED,
            DecisionClassification.REJECTED,
            DecisionClassification.MANUAL_REVIEW,
        ]

    def test_decision_reflects_risk_analysis(self, risky_applicant_application):
        """Test that decision is influenced by risk analysis."""
        risk_agent = FinancialRiskAnalysisAgent()
        decision_agent = LoanDecisionAgent()
        applicant_agent = ApplicantProfileAgent()

        # Get analyses
        applicant_result = applicant_agent.analyze(
            applicant=risky_applicant_application.applicant_profile,
            employment=risky_applicant_application.employment_info,
            credit=risky_applicant_application.credit_record,
        )

        risk_result = risk_agent.analyze(risky_applicant_application)

        # Make decision
        decision = decision_agent.decide(
            application=risky_applicant_application,
            applicant_analysis=applicant_result,
            risk_analysis=risk_result,
        )

        # High risk should not result in approved decision
        if risk_result["risk_score"] > 70:
            assert decision["classification"] != DecisionClassification.APPROVED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
