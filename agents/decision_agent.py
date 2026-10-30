"""Loan Decision Agent for synthesizing multi-factor approval decisions."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import anthropic

from models.schemas import (
    DecisionClassification,
    LoanApplicationRequest,
)
from shared.config import get_settings
from shared.logger import get_logger
from shared.exceptions import AgentException, ValidationException


logger = get_logger("decision_agent")


@dataclass
class DecisionResult:
    """Structured result from decision synthesis."""

    classification: DecisionClassification
    confidence_score: float
    reasoning: str
    risk_factors: List[str]
    positive_factors: List[str]
    recommended_interest_rate: Optional[float]
    conditions: List[str]
    decided_at: datetime


class LoanDecisionAgent:
    """Agent for synthesizing loan approval decisions based on multi-factor analysis."""

    # Decision thresholds (0-100 risk score scale)
    RISK_THRESHOLD_APPROVE = 35
    RISK_THRESHOLD_REVIEW = 65
    RISK_THRESHOLD_REJECT = 80

    # Confidence score factors
    MIN_CONFIDENCE = 0.5
    MAX_CONFIDENCE = 0.99

    def __init__(self):
        """Initialize the loan decision agent."""
        settings = get_settings()

        if not settings.langsmith_api_key:
            raise AgentException(
                "LANGSMITH_API_KEY not configured",
                agent_name="LoanDecisionAgent",
            )

        self.client = anthropic.Anthropic(
            api_key=settings.langsmith_api_key,
            base_url=settings.langsmith_base_url,
        )
        self.model = "global.anthropic.claude-opus-4-5-20251101-v1:0"
        self.timeout = settings.agent_timeout_seconds

        logger.info("LoanDecisionAgent initialized successfully")

    def decide(
        self,
        application: LoanApplicationRequest,
        applicant_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize a loan decision from applicant and risk analysis.

        Args:
            application: The loan application request
            applicant_analysis: Result from ApplicantProfileAgent
            risk_analysis: Result from FinancialRiskAnalysisAgent

        Returns:
            Dict with decision classification, confidence, and reasoning
        """
        try:
            logger.info(
                f"Starting loan decision synthesis for {application.applicant_profile.email}"
            )

            # Step 1: Validate inputs
            self._validate_inputs(application, applicant_analysis, risk_analysis)

            # Step 2: Calculate base decision from risk score
            risk_score = risk_analysis.get("risk_score", 50)
            base_classification = self._classify_by_risk(risk_score)

            # Step 3: Calculate confidence score
            confidence = self._calculate_confidence(
                applicant_analysis, risk_analysis, risk_score
            )

            # Step 4: Extract key factors
            risk_factors = self._extract_risk_factors(
                applicant_analysis, risk_analysis
            )
            positive_factors = risk_analysis.get("positive_factors", [])

            # Step 5: Use Claude for complex reasoning
            claude_reasoning = self._get_claude_reasoning(
                application=application,
                applicant_analysis=applicant_analysis,
                risk_analysis=risk_analysis,
                base_classification=base_classification,
                risk_score=risk_score,
                risk_factors=risk_factors,
                positive_factors=positive_factors,
            )

            # Step 6: Apply Claude insights to override/refine decision if needed
            final_classification, adjusted_confidence = (
                self._apply_claude_insights(
                    base_classification,
                    confidence,
                    claude_reasoning,
                    risk_factors,
                    positive_factors,
                )
            )

            # Step 7: Calculate recommended interest rate
            recommended_rate = self._calculate_interest_rate(
                risk_score, application.loan_details.interest_rate
            )

            # Step 8: Extract conditions
            conditions = self._extract_conditions(
                final_classification, risk_factors, risk_score
            )

            # Compile results
            result = self._compile_result(
                classification=final_classification,
                confidence_score=adjusted_confidence,
                reasoning=claude_reasoning,
                risk_factors=risk_factors,
                positive_factors=positive_factors,
                recommended_interest_rate=recommended_rate,
                conditions=conditions,
            )

            logger.info(
                f"Loan decision completed for {application.applicant_profile.email}",
                extra={
                    "classification": final_classification,
                    "confidence": adjusted_confidence,
                    "risk_score": risk_score,
                },
            )

            return result

        except ValidationException as e:
            logger.error(f"Validation error in decision synthesis: {str(e)}")
            raise AgentException(
                f"Validation failed: {str(e)}",
                agent_name="LoanDecisionAgent",
            )
        except Exception as e:
            logger.error(
                f"Error synthesizing loan decision: {str(e)}", exc_info=True
            )
            raise AgentException(
                f"Failed to synthesize decision: {str(e)}",
                agent_name="LoanDecisionAgent",
            )

    def _validate_inputs(
        self,
        application: LoanApplicationRequest,
        applicant_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
    ) -> None:
        """Validate that all required inputs are present."""
        if not application:
            raise ValidationException("Application is required")
        if not applicant_analysis:
            raise ValidationException("Applicant analysis is required")
        if not risk_analysis:
            raise ValidationException("Risk analysis is required")

        required_applicant_fields = [
            "validation_status",
            "income_stability_score",
            "employment_risk_score",
        ]
        for field in required_applicant_fields:
            if field not in applicant_analysis:
                raise ValidationException(
                    f"Missing required field in applicant analysis: {field}"
                )

        required_risk_fields = ["risk_score", "dti_ratio", "credit_risk"]
        for field in required_risk_fields:
            if field not in risk_analysis:
                raise ValidationException(
                    f"Missing required field in risk analysis: {field}"
                )

    def _classify_by_risk(self, risk_score: float) -> DecisionClassification:
        """Classify decision based on risk score alone.

        Risk Score Thresholds:
        - 0-35: Approve
        - 35-65: Manual Review
        - 65-100: Reject
        """
        if risk_score < self.RISK_THRESHOLD_APPROVE:
            return DecisionClassification.APPROVED
        elif risk_score < self.RISK_THRESHOLD_REVIEW:
            return DecisionClassification.MANUAL_REVIEW
        else:
            return DecisionClassification.REJECTED

    def _calculate_confidence(
        self,
        applicant_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        risk_score: float,
    ) -> float:
        """Calculate confidence score based on data quality and consistency.

        Factors considered:
        - Profile completeness
        - Consistency between applicant and risk profiles
        - Risk score extremeness (very high/low = higher confidence)
        """
        confidence = 0.7  # Base confidence

        # Factor 1: Profile completeness (0.05 points per 10% completeness)
        completeness = applicant_analysis.get("profile_completeness", 0)
        confidence += (completeness / 200)  # Max +0.5

        # Factor 2: Consistency between employment and income stability
        employment_risk = applicant_analysis.get("employment_risk_score", 50)
        if employment_risk < 30 and risk_analysis.get("dti_risk_level") == "low":
            confidence += 0.1
        elif employment_risk > 70 and risk_analysis.get("dti_risk_level") == "high":
            confidence += 0.1

        # Factor 3: Risk score extremeness
        if risk_score < 20 or risk_score > 80:
            confidence += 0.05

        # Factor 4: Anomalies reduce confidence
        anomalies = applicant_analysis.get("anomalies", [])
        confidence -= len(anomalies) * 0.05

        # Cap at reasonable ranges
        return max(self.MIN_CONFIDENCE, min(confidence, self.MAX_CONFIDENCE))

    def _extract_risk_factors(
        self,
        applicant_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
    ) -> List[str]:
        """Extract and deduplicate risk factors from both analyses."""
        risk_factors = set()

        # From applicant analysis
        risk_factors.update(applicant_analysis.get("anomalies", []))
        risk_factors.update(applicant_analysis.get("warnings", []))
        risk_factors.update(applicant_analysis.get("critical_issues", []))

        # From risk analysis
        risk_factors.update(risk_analysis.get("risk_factors", []))
        risk_factors.update(risk_analysis.get("anomalies", []))

        return list(risk_factors)

    def _get_claude_reasoning(
        self,
        application: LoanApplicationRequest,
        applicant_analysis: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        base_classification: DecisionClassification,
        risk_score: float,
        risk_factors: List[str],
        positive_factors: List[str],
    ) -> str:
        """Use Claude to generate comprehensive decision reasoning."""
        try:
            system_prompt = """You are an expert loan underwriter synthesizing a final approval decision.
Your task is to review all analysis and provide concise, professional reasoning for the decision.
Consider:
1. The quantitative risk score and what it means
2. Key risk factors that drove the decision
3. Positive factors that might mitigate risks
4. Any special considerations or nuances
5. Clear recommendation for loan officers

Provide reasoning in 2-3 sentences that is factual, professional, and actionable."""

            summary = f"""
APPLICANT SUMMARY:
- Name: {application.applicant_profile.first_name} {application.applicant_profile.last_name}
- Loan Amount: ${application.loan_details.loan_amount:,.2f}
- Loan Purpose: {application.loan_details.loan_purpose}
- Annual Income: ${application.employment_info.annual_income:,.2f}
- Credit Score: {application.credit_record.credit_score}

ANALYSIS RESULTS:
- Overall Risk Score: {risk_score:.0f}/100
- Base Decision: {base_classification.value}
- Applicant Status: {applicant_analysis.get('validation_status', 'unknown')}
- Income Stability: {applicant_analysis.get('income_stability_level', 'unknown')}
- Employment Risk: {applicant_analysis.get('employment_risk_level', 'unknown')}
- DTI Risk Level: {risk_analysis.get('dti_risk_level', 'unknown')}
- DTI Ratio: {risk_analysis.get('dti_ratio', 'unknown'):.1f}%

KEY RISK FACTORS ({len(risk_factors)}):
{chr(10).join(f'- {factor}' for factor in risk_factors[:5])}

POSITIVE FACTORS ({len(positive_factors)}):
{chr(10).join(f'- {factor}' for factor in positive_factors[:3]) if positive_factors else '- None identified'}

Please provide the final decision reasoning based on this analysis."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": summary,
                    }
                ]
            )

            reasoning = response.content[0].text.strip()
            logger.debug(
                f"Claude reasoning generated",
                extra={"reasoning_length": len(reasoning)},
            )

            return reasoning

        except Exception as e:
            logger.warning(
                f"Failed to generate Claude reasoning: {str(e)}, using fallback"
            )
            # Fallback reasoning
            return (
                f"Applicant {base_classification.value} based on overall risk score "
                f"of {risk_score:.0f}/100. Manual review recommended for final approval."
            )

    def _apply_claude_insights(
        self,
        base_classification: DecisionClassification,
        confidence: float,
        claude_reasoning: str,
        risk_factors: List[str],
        positive_factors: List[str],
    ) -> tuple:
        """Apply Claude insights to potentially override base classification."""
        # If we have strong positive factors and base is marginal, consider upgrading
        if (
            base_classification == DecisionClassification.MANUAL_REVIEW
            and len(positive_factors) >= 3
            and len(risk_factors) <= 2
        ):
            logger.info("Upgrading to APPROVED based on strong positive factors")
            return DecisionClassification.APPROVED, min(confidence + 0.1, 0.95)

        # If we have multiple critical risk factors, consider downgrading
        critical_factors = [f for f in risk_factors if "critical" in f.lower()]
        if (
            base_classification == DecisionClassification.MANUAL_REVIEW
            and len(critical_factors) >= 3
        ):
            logger.info("Downgrading to REJECTED based on critical risk factors")
            return DecisionClassification.REJECTED, min(confidence, 0.85)

        return base_classification, confidence

    def _calculate_interest_rate(
        self, risk_score: float, base_rate: Optional[float] = None
    ) -> Optional[float]:
        """Calculate recommended interest rate based on risk score.

        Risk-based pricing:
        - 0-25: Base rate or prime
        - 25-50: Base + 1-2%
        - 50-75: Base + 3-5%
        - 75-100: Base + 6-8% or unsecured prime
        """
        if base_rate is None:
            return None

        if risk_score < 25:
            return base_rate
        elif risk_score < 50:
            return base_rate + 1.5
        elif risk_score < 75:
            return base_rate + 4.0
        else:
            return base_rate + 7.0

    def _extract_conditions(
        self,
        classification: DecisionClassification,
        risk_factors: List[str],
        risk_score: float,
    ) -> List[str]:
        """Extract conditions and requirements based on decision."""
        conditions = []

        if classification == DecisionClassification.APPROVED:
            if risk_score > 25:
                conditions.append("Require proof of income stability")
            if "recent_employment" in str(risk_factors).lower():
                conditions.append("Proof of continuous employment required")

        elif classification == DecisionClassification.MANUAL_REVIEW:
            conditions.append("Manual underwriter review required")
            if risk_score > 60:
                conditions.append("Co-signer consideration recommended")

        elif classification == DecisionClassification.REJECTED:
            conditions.append("Application declined - reapply in 12 months")
            if risk_score > 90:
                conditions.append("Consider debt consolidation before reapplication")

        return conditions

    def _compile_result(
        self,
        classification: DecisionClassification,
        confidence_score: float,
        reasoning: str,
        risk_factors: List[str],
        positive_factors: List[str],
        recommended_interest_rate: Optional[float],
        conditions: List[str],
    ) -> Dict[str, Any]:
        """Compile all decision results into final output."""
        return {
            "classification": classification,
            "classification_value": classification.value,
            "confidence_score": confidence_score,
            "reasoning": reasoning,
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "recommended_interest_rate": recommended_interest_rate,
            "conditions": conditions,
            "decided_at": datetime.utcnow().isoformat(),
        }


# Singleton instance
_decision_agent: Optional[LoanDecisionAgent] = None


def get_decision_agent() -> LoanDecisionAgent:
    """Get or create the decision agent singleton."""
    global _decision_agent
    if _decision_agent is None:
        _decision_agent = LoanDecisionAgent()
    return _decision_agent
