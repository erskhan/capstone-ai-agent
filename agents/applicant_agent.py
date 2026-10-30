"""Applicant Profile Agent for loan approval system.

This agent validates applicant data, calculates income stability and employment risk scores,
summarizes credit history, and detects data anomalies using Claude AI for complex reasoning.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import anthropic

from models.schemas import (
    ApplicantProfile,
    EmploymentInfo,
    CreditRecord,
    EmploymentType,
)
from shared.config import get_settings
from shared.logger import get_logger
from shared.exceptions import AgentException, ValidationException


logger = get_logger("applicant_agent")


class IncomeStabilityLevel(str, Enum):
    """Income stability classification."""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class EmploymentRiskLevel(str, Enum):
    """Employment risk classification."""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ApplicantProfileResult:
    """Structured result from applicant profile analysis."""

    validation_status: str  # "valid", "incomplete", "invalid"
    income_stability_score: float  # 0-100
    income_stability_level: IncomeStabilityLevel
    employment_risk_score: float  # 0-100
    employment_risk_level: EmploymentRiskLevel
    credit_summary: Dict[str, Any]
    anomalies: List[str]
    reasoning: str
    profile_completeness: float  # 0-100 percentage
    critical_issues: List[str]
    warnings: List[str]
    analyzed_at: datetime


class ApplicantProfileAgent:
    """Agent for analyzing and validating applicant profiles."""

    def __init__(self):
        """Initialize the applicant profile agent."""
        settings = get_settings()

        if not settings.langsmith_api_key:
            raise AgentException(
                "LANGSMITH_API_KEY not configured",
                agent_name="ApplicantProfileAgent",
            )

        self.client = anthropic.Anthropic(
            api_key=settings.langsmith_api_key,
            base_url=settings.langsmith_base_url,
        )
        self.model = "global.anthropic.claude-opus-4-5-20251101-v1:0"
        self.timeout = settings.agent_timeout_seconds

        logger.info("ApplicantProfileAgent initialized successfully")

    def analyze(
        self,
        applicant: ApplicantProfile,
        employment: EmploymentInfo,
        credit: CreditRecord,
    ) -> Dict[str, Any]:
        """Analyze applicant profile and return structured result.

        Args:
            applicant: ApplicantProfile data
            employment: EmploymentInfo data
            credit: CreditRecord data

        Returns:
            Dict with analysis results including scores and flags
        """
        try:
            logger.info(
                f"Starting applicant profile analysis for {applicant.email}"
            )

            # Step 1: Validate data completeness
            validation_result = self._validate_data_completeness(
                applicant, employment, credit
            )

            # Step 2: Calculate income stability score
            income_stability = self._calculate_income_stability_score(
                employment, credit
            )

            # Step 3: Assess employment risk
            employment_risk = self._assess_employment_risk(employment, credit)

            # Step 4: Summarize credit history
            credit_summary = self._summarize_credit_history(credit)

            # Step 5: Check for data anomalies
            anomalies = self._check_data_anomalies(
                applicant, employment, credit
            )

            # Step 6: Use Claude AI for complex reasoning
            reasoning = self._get_ai_reasoning(
                applicant=applicant,
                employment=employment,
                credit=credit,
                income_stability=income_stability,
                employment_risk=employment_risk,
                anomalies=anomalies,
            )

            # Compile results
            result = self._compile_result(
                validation_result=validation_result,
                income_stability=income_stability,
                employment_risk=employment_risk,
                credit_summary=credit_summary,
                anomalies=anomalies,
                reasoning=reasoning,
            )

            logger.info(
                f"Applicant profile analysis completed for {applicant.email}",
                extra={
                    "validation_status": result["validation_status"],
                    "income_stability_score": result["income_stability_score"],
                    "employment_risk_score": result["employment_risk_score"],
                },
            )

            return result

        except ValidationException as e:
            logger.error(f"Validation error in applicant analysis: {str(e)}")
            raise AgentException(
                f"Validation failed: {str(e)}",
                agent_name="ApplicantProfileAgent",
            )
        except Exception as e:
            logger.error(
                f"Error analyzing applicant profile: {str(e)}", exc_info=True
            )
            raise AgentException(
                f"Failed to analyze applicant profile: {str(e)}",
                agent_name="ApplicantProfileAgent",
            )

    def _validate_data_completeness(
        self,
        applicant: ApplicantProfile,
        employment: EmploymentInfo,
        credit: CreditRecord,
    ) -> Dict[str, Any]:
        """Validate that all required data is present and valid.

        Returns:
            Dict with validation_status, completeness_percentage, and issues
        """
        issues = []
        required_fields_checked = 0
        required_fields_valid = 0

        # Check applicant profile
        applicant_fields = [
            ("first_name", applicant.first_name),
            ("last_name", applicant.last_name),
            ("email", applicant.email),
            ("phone", applicant.phone),
            ("date_of_birth", applicant.date_of_birth),
            ("ssn", applicant.ssn),
            ("address", applicant.address),
            ("city", applicant.city),
            ("state", applicant.state),
            ("zip_code", applicant.zip_code),
        ]

        for field_name, field_value in applicant_fields:
            required_fields_checked += 1
            if field_value and str(field_value).strip():
                required_fields_valid += 1
            else:
                issues.append(f"Missing applicant field: {field_name}")

        # Check employment info
        employment_fields = [
            ("employment_type", employment.employment_type),
            ("employer_name", employment.employer_name),
            ("job_title", employment.job_title),
            ("years_employed", employment.years_employed),
            ("annual_income", employment.annual_income),
        ]

        for field_name, field_value in employment_fields:
            required_fields_checked += 1
            if field_value is not None and (
                isinstance(field_value, (int, float)) or str(field_value).strip()
            ):
                required_fields_valid += 1
            else:
                issues.append(f"Missing employment field: {field_name}")

        # Check credit record
        credit_fields = [
            ("credit_score", credit.credit_score),
            ("years_of_credit_history", credit.years_of_credit_history),
            ("number_of_accounts", credit.number_of_accounts),
            ("delinquencies_last_24_months", credit.delinquencies_last_24_months),
            ("public_records", credit.public_records),
            ("current_debt", credit.current_debt),
        ]

        for field_name, field_value in credit_fields:
            required_fields_checked += 1
            if field_value is not None:
                required_fields_valid += 1
            else:
                issues.append(f"Missing credit field: {field_name}")

        completeness_percentage = (
            (required_fields_valid / required_fields_checked * 100)
            if required_fields_checked > 0
            else 0
        )

        validation_status = "valid"
        if completeness_percentage < 80:
            validation_status = "incomplete"
        if len(issues) > 5:
            validation_status = "invalid"

        return {
            "validation_status": validation_status,
            "completeness_percentage": completeness_percentage,
            "issues": issues,
            "fields_checked": required_fields_checked,
            "fields_valid": required_fields_valid,
        }

    def _calculate_income_stability_score(
        self,
        employment: EmploymentInfo,
        credit: CreditRecord,
    ) -> Dict[str, Any]:
        """Calculate income stability score based on employment duration and consistency.

        Returns:
            Dict with score (0-100), level, and contributing factors
        """
        score_components = []

        # Factor 1: Employment duration (0-30 points)
        # Very stable: 5+ years (30 points)
        # Stable: 2-5 years (20 points)
        # Moderate: 6-24 months (10 points)
        # Unstable: < 6 months (0 points)
        employment_duration_score = 0
        if employment.years_employed >= 5:
            employment_duration_score = 30
        elif employment.years_employed >= 2:
            employment_duration_score = 20
        elif employment.years_employed >= 1:
            employment_duration_score = 10
        else:
            employment_duration_score = 0

        score_components.append(
            {
                "factor": "Employment Duration",
                "years": employment.years_employed,
                "score": employment_duration_score,
                "max_points": 30,
            }
        )

        # Factor 2: Income consistency via employment type (0-25 points)
        employment_stability_score = self._get_employment_type_stability_score(
            employment.employment_type
        )
        score_components.append(
            {
                "factor": "Employment Type Stability",
                "type": employment.employment_type,
                "score": employment_stability_score,
                "max_points": 25,
            }
        )

        # Factor 3: Credit history length (0-25 points)
        # Excellent: 10+ years (25 points)
        # Good: 5-10 years (15 points)
        # Fair: 2-5 years (10 points)
        # Limited: < 2 years (5 points)
        credit_history_score = 0
        if credit.years_of_credit_history >= 10:
            credit_history_score = 25
        elif credit.years_of_credit_history >= 5:
            credit_history_score = 15
        elif credit.years_of_credit_history >= 2:
            credit_history_score = 10
        elif credit.years_of_credit_history > 0:
            credit_history_score = 5
        else:
            credit_history_score = 0

        score_components.append(
            {
                "factor": "Credit History Length",
                "years": credit.years_of_credit_history,
                "score": credit_history_score,
                "max_points": 25,
            }
        )

        # Factor 4: Account management (0-20 points)
        # No delinquencies: 20 points
        # 1-2 delinquencies: 10 points
        # 3+ delinquencies: 0 points
        account_management_score = 0
        if credit.delinquencies_last_24_months == 0:
            account_management_score = 20
        elif credit.delinquencies_last_24_months <= 2:
            account_management_score = 10
        else:
            account_management_score = 0

        score_components.append(
            {
                "factor": "Account Management",
                "delinquencies_24m": credit.delinquencies_last_24_months,
                "score": account_management_score,
                "max_points": 20,
            }
        )

        total_score = sum(
            component["score"] for component in score_components
        )

        # Determine income stability level
        if total_score >= 90:
            level = IncomeStabilityLevel.VERY_HIGH
        elif total_score >= 75:
            level = IncomeStabilityLevel.HIGH
        elif total_score >= 50:
            level = IncomeStabilityLevel.MODERATE
        elif total_score >= 25:
            level = IncomeStabilityLevel.LOW
        else:
            level = IncomeStabilityLevel.VERY_LOW

        return {
            "score": total_score,
            "level": level,
            "components": score_components,
        }

    def _get_employment_type_stability_score(
        self, employment_type: EmploymentType
    ) -> int:
        """Get stability score based on employment type."""
        stability_map = {
            EmploymentType.FULL_TIME: 25,
            EmploymentType.PART_TIME: 10,
            EmploymentType.SELF_EMPLOYED: 15,
            EmploymentType.RETIRED: 20,
            EmploymentType.STUDENT: 0,
            EmploymentType.UNEMPLOYED: 0,
        }
        return stability_map.get(employment_type, 0)

    def _assess_employment_risk(
        self,
        employment: EmploymentInfo,
        credit: CreditRecord,
    ) -> Dict[str, Any]:
        """Assess employment-related risk factors.

        Returns:
            Dict with risk_score (0-100), level, and risk factors
        """
        risk_factors = []
        risk_score = 0

        # Factor 1: Employment type risk (base 0-25 points)
        employment_type_risk = self._get_employment_type_risk_score(
            employment.employment_type
        )
        risk_score += employment_type_risk
        if employment_type_risk > 15:
            risk_factors.append(
                f"High-risk employment type: {employment.employment_type}"
            )

        # Factor 2: Job stability (0-25 points)
        # Recent job change = higher risk
        if employment.years_employed < 0.5:
            risk_score += 25
            risk_factors.append(
                "Very recent employment change (< 6 months)"
            )
        elif employment.years_employed < 1:
            risk_score += 15
            risk_factors.append("Recent employment change (< 1 year)")
        elif employment.years_employed < 2:
            risk_score += 10
            risk_factors.append("Relatively recent employment (1-2 years)")

        # Factor 3: Income adequacy relative to debt (0-25 points)
        monthly_income = employment.monthly_income or (
            employment.annual_income / 12
        )
        monthly_debt = credit.current_debt / 12 if credit.current_debt > 0 else 0
        debt_to_income_ratio = (
            monthly_debt / monthly_income if monthly_income > 0 else 1
        )

        if debt_to_income_ratio > 0.5:
            risk_score += 25
            risk_factors.append(
                f"Very high debt-to-income ratio: {debt_to_income_ratio:.2f}"
            )
        elif debt_to_income_ratio > 0.35:
            risk_score += 15
            risk_factors.append(
                f"High debt-to-income ratio: {debt_to_income_ratio:.2f}"
            )
        elif debt_to_income_ratio > 0.25:
            risk_score += 5
            risk_factors.append(
                f"Moderate debt-to-income ratio: {debt_to_income_ratio:.2f}"
            )

        # Factor 4: Recent delinquencies (0-25 points)
        if credit.delinquencies_last_24_months >= 3:
            risk_score += 25
            risk_factors.append(
                f"Multiple recent delinquencies: {credit.delinquencies_last_24_months}"
            )
        elif credit.delinquencies_last_24_months == 2:
            risk_score += 15
            risk_factors.append(
                "Two delinquencies in last 24 months"
            )
        elif credit.delinquencies_last_24_months == 1:
            risk_score += 5
            risk_factors.append(
                "One delinquency in last 24 months"
            )

        # Normalize score to 0-100 range
        employment_risk_score = min(risk_score, 100)

        # Determine employment risk level
        if employment_risk_score >= 75:
            risk_level = EmploymentRiskLevel.VERY_HIGH
        elif employment_risk_score >= 60:
            risk_level = EmploymentRiskLevel.HIGH
        elif employment_risk_score >= 40:
            risk_level = EmploymentRiskLevel.MODERATE
        elif employment_risk_score >= 20:
            risk_level = EmploymentRiskLevel.LOW
        else:
            risk_level = EmploymentRiskLevel.VERY_LOW

        return {
            "score": employment_risk_score,
            "level": risk_level,
            "risk_factors": risk_factors,
            "debt_to_income_ratio": debt_to_income_ratio,
        }

    def _get_employment_type_risk_score(
        self, employment_type: EmploymentType
    ) -> int:
        """Get risk score based on employment type."""
        risk_map = {
            EmploymentType.FULL_TIME: 0,
            EmploymentType.RETIRED: 5,
            EmploymentType.PART_TIME: 10,
            EmploymentType.SELF_EMPLOYED: 15,
            EmploymentType.STUDENT: 20,
            EmploymentType.UNEMPLOYED: 25,
        }
        return risk_map.get(employment_type, 15)

    def _summarize_credit_history(self, credit: CreditRecord) -> Dict[str, Any]:
        """Summarize credit history information.

        Returns:
            Dict with credit summary including score, account info, and flags
        """
        credit_score = credit.credit_score

        # Determine credit score category
        if credit_score >= 750:
            score_category = "Excellent"
            score_risk = "Very Low"
        elif credit_score >= 700:
            score_category = "Good"
            score_risk = "Low"
        elif credit_score >= 650:
            score_category = "Fair"
            score_risk = "Moderate"
        elif credit_score >= 600:
            score_category = "Poor"
            score_risk = "High"
        else:
            score_category = "Very Poor"
            score_risk = "Very High"

        # Analyze account health
        account_health = "Healthy"
        if credit.delinquencies_last_24_months > 0:
            account_health = "At Risk"
        if credit.public_records > 0:
            account_health = "Compromised"

        return {
            "score": credit_score,
            "score_category": score_category,
            "score_risk_level": score_risk,
            "years_of_history": credit.years_of_credit_history,
            "number_of_accounts": credit.number_of_accounts,
            "current_debt": credit.current_debt,
            "recent_delinquencies": credit.delinquencies_last_24_months,
            "public_records": credit.public_records,
            "account_health": account_health,
        }

    def _check_data_anomalies(
        self,
        applicant: ApplicantProfile,
        employment: EmploymentInfo,
        credit: CreditRecord,
    ) -> List[str]:
        """Check for data anomalies and inconsistencies.

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Anomaly 1: Age inconsistency
        try:
            dob = datetime.strptime(applicant.date_of_birth, "%Y-%m-%d")
            age = (datetime.now() - dob).days / 365.25
            if age < 18:
                anomalies.append(
                    "Applicant age below minimum (18 years old required)"
                )
            elif age > 120:
                anomalies.append("Applicant age appears invalid (> 120 years)")
        except ValueError:
            anomalies.append("Invalid date of birth format")

        # Anomaly 2: Employment duration inconsistency
        if employment.years_employed > 70:
            anomalies.append(
                "Employment duration unreasonably long (> 70 years)"
            )

        # Anomaly 3: Income too high relative to employment type
        if employment.employment_type == EmploymentType.STUDENT:
            if employment.annual_income > 50000:
                anomalies.append(
                    "Unusually high income for student employment"
                )
        elif employment.employment_type == EmploymentType.PART_TIME:
            if employment.annual_income > 100000:
                anomalies.append(
                    "Unusually high income for part-time employment"
                )

        # Anomaly 4: Credit score inconsistency
        if credit.credit_score >= 750 and credit.delinquencies_last_24_months > 2:
            anomalies.append(
                "High credit score with recent delinquencies (inconsistent)"
            )

        # Anomaly 5: Credit history inconsistency
        if credit.years_of_credit_history > 0 and credit.number_of_accounts == 0:
            anomalies.append(
                "Credit history exists but no credit accounts reported"
            )

        # Anomaly 6: Too many public records for credit score
        if credit.public_records > 0 and credit.credit_score > 700:
            anomalies.append(
                "Public records present with relatively high credit score"
            )

        # Anomaly 7: Debt inconsistency
        if credit.current_debt > 0 and credit.number_of_accounts == 0:
            anomalies.append("Current debt reported but no credit accounts")

        # Anomaly 8: Monthly vs annual income consistency
        if (
            employment.monthly_income
            and employment.annual_income
        ):
            calculated_annual = employment.monthly_income * 12
            variance = abs(
                (calculated_annual - employment.annual_income)
                / employment.annual_income
            )
            if variance > 0.05:  # More than 5% variance
                anomalies.append(
                    f"Monthly and annual income mismatch (variance: {variance:.1%})"
                )

        return anomalies

    def _get_ai_reasoning(
        self,
        applicant: ApplicantProfile,
        employment: EmploymentInfo,
        credit: CreditRecord,
        income_stability: Dict[str, Any],
        employment_risk: Dict[str, Any],
        anomalies: List[str],
    ) -> str:
        """Use Claude AI to generate complex reasoning about applicant profile.

        Returns:
            Reasoning string from Claude
        """
        try:
            system_prompt = """You are an expert loan officer with extensive experience in credit analysis and risk assessment.
Your task is to analyze an applicant's profile and provide professional, concise reasoning about their creditworthiness.
Focus on:
1. Income stability and reliability
2. Employment risk factors
3. Credit history patterns
4. Overall financial health indicators
5. Any red flags or concerns

Provide a balanced, factual assessment in 2-3 sentences."""

            applicant_summary = f"""
Applicant: {applicant.first_name} {applicant.last_name}
Age: {applicant.date_of_birth}
Location: {applicant.city}, {applicant.state}

Employment: {employment.employment_type.value} at {employment.employer_name}
Position: {employment.job_title}
Duration: {employment.years_employed:.1f} years
Annual Income: ${employment.annual_income:,.2f}

Credit Score: {credit.credit_score} ({credit.credit_score_risk_level if hasattr(credit, 'credit_score_risk_level') else 'N/A'})
Credit History: {credit.years_of_credit_history} years
Active Accounts: {credit.number_of_accounts}
Recent Delinquencies: {credit.delinquencies_last_24_months}
Public Records: {credit.public_records}
Current Debt: ${credit.current_debt:,.2f}

Income Stability Score: {income_stability['score']:.0f}/100 ({income_stability['level'].value})
Employment Risk Score: {employment_risk['score']:.0f}/100 ({employment_risk['level'].value})

Detected Issues: {', '.join(anomalies) if anomalies else 'None'}
"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze this applicant profile and provide professional reasoning about their creditworthiness:\n\n{applicant_summary}"
                    }
                ]
            )

            reasoning = response.content[0].text.strip()
            logger.debug(
                f"AI reasoning generated for {applicant.email}",
                extra={"reasoning_length": len(reasoning)},
            )

            return reasoning

        except Exception as e:
            logger.warning(
                f"Failed to generate AI reasoning: {str(e)}, using fallback"
            )
            # Fallback reasoning if Claude API fails
            return (
                "Unable to generate detailed AI reasoning at this time. "
                "Manual review recommended."
            )

    def _compile_result(
        self,
        validation_result: Dict[str, Any],
        income_stability: Dict[str, Any],
        employment_risk: Dict[str, Any],
        credit_summary: Dict[str, Any],
        anomalies: List[str],
        reasoning: str,
    ) -> Dict[str, Any]:
        """Compile all analysis results into final output.

        Returns:
            Dict with all analysis results
        """
        critical_issues = []
        warnings = []

        # Determine critical issues
        if validation_result["validation_status"] == "invalid":
            critical_issues.append("Application data is invalid")
        if validation_result["validation_status"] == "incomplete":
            warnings.append(
                f"Application data is incomplete ({validation_result['completeness_percentage']:.0f}%)"
            )

        if employment_risk["score"] >= 75:
            critical_issues.append(
                f"Very high employment risk (score: {employment_risk['score']:.0f})"
            )
        elif employment_risk["score"] >= 60:
            warnings.append(
                f"High employment risk (score: {employment_risk['score']:.0f})"
            )

        if credit_summary["score"] < 600:
            critical_issues.append(
                f"Poor credit score ({credit_summary['score']})"
            )
        elif credit_summary["score"] < 650:
            warnings.append(
                f"Fair credit score ({credit_summary['score']})"
            )

        if len(anomalies) >= 3:
            critical_issues.append(
                f"Multiple data anomalies detected ({len(anomalies)})"
            )
        elif len(anomalies) > 0:
            warnings.append(f"Data anomalies detected ({len(anomalies)})")

        return {
            "validation_status": validation_result["validation_status"],
            "income_stability_score": income_stability["score"],
            "income_stability_level": income_stability["level"].value,
            "employment_risk_score": employment_risk["score"],
            "employment_risk_level": employment_risk["level"].value,
            "credit_summary": credit_summary,
            "anomalies": anomalies,
            "reasoning": reasoning,
            "profile_completeness": validation_result["completeness_percentage"],
            "critical_issues": critical_issues,
            "warnings": warnings,
            "analyzed_at": datetime.utcnow().isoformat(),
        }
