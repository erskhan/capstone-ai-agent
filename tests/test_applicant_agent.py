"""Tests for the Applicant Profile Agent."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from models.schemas import (
    ApplicantProfile,
    EmploymentInfo,
    CreditRecord,
    EmploymentType,
)
from agents.applicant_agent import (
    ApplicantProfileAgent,
    IncomeStabilityLevel,
    EmploymentRiskLevel,
)
from shared.exceptions import AgentException


class TestApplicantProfileAgent:
    """Test cases for ApplicantProfileAgent."""

    @pytest.fixture
    def valid_applicant(self) -> ApplicantProfile:
        """Create a valid applicant profile."""
        return ApplicantProfile(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="555-123-4567",
            date_of_birth="1985-03-15",
            ssn="123-45-6789",
            address="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
        )

    @pytest.fixture
    def valid_employment(self) -> EmploymentInfo:
        """Create valid employment info."""
        return EmploymentInfo(
            employment_type=EmploymentType.FULL_TIME,
            employer_name="Acme Corporation",
            job_title="Software Engineer",
            years_employed=5.5,
            annual_income=120000.0,
            monthly_income=10000.0,
        )

    @pytest.fixture
    def valid_credit(self) -> CreditRecord:
        """Create valid credit record."""
        return CreditRecord(
            credit_score=750,
            years_of_credit_history=10.0,
            number_of_accounts=5,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=15000.0,
        )

    @pytest.fixture
    def risky_applicant(self) -> ApplicantProfile:
        """Create a risky applicant profile."""
        return ApplicantProfile(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="555-987-6543",
            date_of_birth="1990-06-20",
            ssn="987-65-4321",
            address="456 Oak Ave",
            city="Chicago",
            state="IL",
            zip_code="60601",
        )

    @pytest.fixture
    def risky_employment(self) -> EmploymentInfo:
        """Create risky employment info."""
        return EmploymentInfo(
            employment_type=EmploymentType.SELF_EMPLOYED,
            employer_name="Self Employed",
            job_title="Freelancer",
            years_employed=0.3,
            annual_income=35000.0,
            monthly_income=2916.67,
        )

    @pytest.fixture
    def risky_credit(self) -> CreditRecord:
        """Create risky credit record."""
        return CreditRecord(
            credit_score=580,
            years_of_credit_history=2.0,
            number_of_accounts=2,
            delinquencies_last_24_months=2,
            public_records=1,
            current_debt=45000.0,
        )

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_agent_initialization(self, mock_llm):
        """Test agent initialization."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            assert agent.llm is not None

    @patch("shared.config.get_settings")
    def test_agent_initialization_missing_api_key(self, mock_settings):
        """Test agent initialization with missing API key."""
        mock_settings.return_value.anthropic_api_key = ""

        with pytest.raises(AgentException) as exc_info:
            ApplicantProfileAgent()

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_validate_data_completeness_valid(
        self,
        mock_llm,
        valid_applicant,
        valid_employment,
        valid_credit,
    ):
        """Test data completeness validation with valid data."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            result = agent._validate_data_completeness(
                valid_applicant, valid_employment, valid_credit
            )

            assert result["validation_status"] == "valid"
            assert result["completeness_percentage"] == 100.0
            assert len(result["issues"]) == 0

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_validate_data_completeness_incomplete(
        self, mock_llm, valid_applicant, valid_employment
    ):
        """Test data completeness validation with incomplete data."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            incomplete_credit = CreditRecord(
                credit_score=None,
                years_of_credit_history=None,
                number_of_accounts=None,
                delinquencies_last_24_months=None,
                public_records=None,
                current_debt=None,
            )

            agent = ApplicantProfileAgent()
            result = agent._validate_data_completeness(
                valid_applicant, valid_employment, incomplete_credit
            )

            assert result["validation_status"] == "incomplete"
            assert result["completeness_percentage"] < 100
            assert len(result["issues"]) > 0

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_calculate_income_stability_score_excellent(
        self, mock_llm, valid_employment, valid_credit
    ):
        """Test income stability calculation for excellent profile."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            result = agent._calculate_income_stability_score(
                valid_employment, valid_credit
            )

            assert result["score"] >= 75  # Should be high
            assert result["level"] == IncomeStabilityLevel.HIGH
            assert len(result["components"]) == 4

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_calculate_income_stability_score_poor(
        self, mock_llm, risky_employment, risky_credit
    ):
        """Test income stability calculation for poor profile."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            result = agent._calculate_income_stability_score(
                risky_employment, risky_credit
            )

            assert result["score"] < 50  # Should be low
            assert result["level"] in [
                IncomeStabilityLevel.LOW,
                IncomeStabilityLevel.VERY_LOW,
            ]

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_assess_employment_risk_low(
        self, mock_llm, valid_employment, valid_credit
    ):
        """Test employment risk assessment for good profile."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            result = agent._assess_employment_risk(
                valid_employment, valid_credit
            )

            assert result["score"] < 40
            assert result["level"] in [
                EmploymentRiskLevel.VERY_LOW,
                EmploymentRiskLevel.LOW,
            ]
            assert len(result["risk_factors"]) == 0

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_assess_employment_risk_high(
        self, mock_llm, risky_employment, risky_credit
    ):
        """Test employment risk assessment for risky profile."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            result = agent._assess_employment_risk(
                risky_employment, risky_credit
            )

            assert result["score"] > 40
            assert result["level"] in [
                EmploymentRiskLevel.MODERATE,
                EmploymentRiskLevel.HIGH,
                EmploymentRiskLevel.VERY_HIGH,
            ]
            assert len(result["risk_factors"]) > 0

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_summarize_credit_history(self, mock_llm, valid_credit):
        """Test credit history summarization."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            result = agent._summarize_credit_history(valid_credit)

            assert result["score"] == 750
            assert result["score_category"] == "Good"
            assert result["number_of_accounts"] == 5
            assert result["account_health"] == "Healthy"

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_check_data_anomalies_no_anomalies(
        self,
        mock_llm,
        valid_applicant,
        valid_employment,
        valid_credit,
    ):
        """Test anomaly detection with clean data."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            anomalies = agent._check_data_anomalies(
                valid_applicant, valid_employment, valid_credit
            )

            assert len(anomalies) == 0

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_check_data_anomalies_detected(
        self,
        mock_llm,
        valid_applicant,
        risky_employment,
        risky_credit,
    ):
        """Test anomaly detection with problematic data."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()
            # Create applicant with very old DOB
            old_applicant = ApplicantProfile(
                first_name="Old",
                last_name="Person",
                email="old@example.com",
                phone="555-000-0000",
                date_of_birth="1900-01-01",
                ssn="111-11-1111",
                address="123 Old St",
                city="Oldtown",
                state="CA",
                zip_code="90001",
            )

            anomalies = agent._check_data_anomalies(
                old_applicant, risky_employment, risky_credit
            )

            assert len(anomalies) > 0
            assert any("invalid" in a.lower() for a in anomalies)

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_get_employment_type_stability_score(self, mock_llm):
        """Test employment type stability scoring."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()

            assert (
                agent._get_employment_type_stability_score(
                    EmploymentType.FULL_TIME
                )
                == 25
            )
            assert (
                agent._get_employment_type_stability_score(
                    EmploymentType.PART_TIME
                )
                == 10
            )
            assert (
                agent._get_employment_type_stability_score(
                    EmploymentType.STUDENT
                )
                == 0
            )
            assert (
                agent._get_employment_type_stability_score(
                    EmploymentType.UNEMPLOYED
                )
                == 0
            )

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_get_employment_type_risk_score(self, mock_llm):
        """Test employment type risk scoring."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            agent = ApplicantProfileAgent()

            assert (
                agent._get_employment_type_risk_score(
                    EmploymentType.FULL_TIME
                )
                == 0
            )
            assert (
                agent._get_employment_type_risk_score(
                    EmploymentType.PART_TIME
                )
                == 10
            )
            assert (
                agent._get_employment_type_risk_score(
                    EmploymentType.UNEMPLOYED
                )
                == 25
            )

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_analyze_valid_applicant(
        self,
        mock_llm,
        valid_applicant,
        valid_employment,
        valid_credit,
    ):
        """Test full analysis with valid applicant."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            mock_llm_instance = MagicMock()
            mock_llm_instance.invoke.return_value.content = (
                "This is a well-qualified applicant with stable employment "
                "and excellent credit history."
            )
            mock_llm.return_value = mock_llm_instance

            agent = ApplicantProfileAgent()
            agent.llm = mock_llm_instance

            result = agent.analyze(valid_applicant, valid_employment, valid_credit)

            assert result["validation_status"] == "valid"
            assert "income_stability_score" in result
            assert "employment_risk_score" in result
            assert "credit_summary" in result
            assert "anomalies" in result
            assert "reasoning" in result
            assert "analyzed_at" in result
            assert len(result["critical_issues"]) == 0

    @patch("agents.applicant_agent.ChatAnthropic")
    def test_analyze_risky_applicant(
        self,
        mock_llm,
        risky_applicant,
        risky_employment,
        risky_credit,
    ):
        """Test full analysis with risky applicant."""
        with patch("shared.config.get_settings") as mock_settings:
            mock_settings.return_value.anthropic_api_key = "test-key"
            mock_settings.return_value.agent_timeout_seconds = 30

            mock_llm_instance = MagicMock()
            mock_llm_instance.invoke.return_value.content = (
                "This applicant presents significant risk factors including "
                "recent employment and poor credit history."
            )
            mock_llm.return_value = mock_llm_instance

            agent = ApplicantProfileAgent()
            agent.llm = mock_llm_instance

            result = agent.analyze(risky_applicant, risky_employment, risky_credit)

            assert "income_stability_score" in result
            assert "employment_risk_score" in result
            assert result["employment_risk_score"] > 40
            assert len(result["warnings"]) > 0
