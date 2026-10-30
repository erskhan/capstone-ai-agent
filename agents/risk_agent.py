"""Financial Risk Analysis Agent for loan risk assessment."""

from typing import Optional, Dict, List, Any
from datetime import datetime
import json

import anthropic

from models.schemas import (
    LoanApplicationRequest,
    RiskAssessment,
    CreditRecord,
    EmploymentInfo,
    LoanDetails,
)
from shared.logger import get_logger
from shared.config import get_settings

logger = get_logger("risk_agent")


class FinancialRiskAnalysisAgent:
    """Analyzes financial risk for loan applications."""

    def __init__(self):
        """Initialize the risk analysis agent."""
        settings = get_settings()
        self.client = anthropic.Anthropic(
            api_key=settings.langsmith_api_key,
            base_url=settings.langsmith_base_url,
        )
        self.model = "global.anthropic.claude-opus-4-5-20251101-v1:0"
        self.settings = settings
        logger.info("Financial Risk Analysis Agent initialized")

    def calculate_dti_ratio(
        self, annual_income: float, monthly_debt_obligations: float
    ) -> float:
        """Calculate Debt-to-Income (DTI) ratio.

        Args:
            annual_income: Applicant's annual income
            monthly_debt_obligations: Total monthly debt obligations

        Returns:
            DTI ratio as a percentage
        """
        if annual_income <= 0:
            return 100.0

        monthly_income = annual_income / 12
        if monthly_income <= 0:
            return 100.0

        dti = (monthly_debt_obligations / monthly_income) * 100
        return min(dti, 100.0)  # Cap at 100%

    def assess_dti_risk(self, dti_ratio: float) -> str:
        """Map DTI ratio to risk level.

        Args:
            dti_ratio: The calculated DTI ratio

        Returns:
            Risk level: 'low', 'medium', or 'high'
        """
        if dti_ratio < 36:
            return "low"
        elif dti_ratio <= 43:
            return "medium"
        else:
            return "high"

    def map_credit_score_to_risk(self, credit_score: int) -> tuple[str, float]:
        """Map credit score to risk level and risk factor.

        Args:
            credit_score: The applicant's credit score (300-850)

        Returns:
            Tuple of (risk_level, risk_factor) where risk_factor is 0.0-1.0
        """
        if credit_score >= 750:
            return "low", 0.1
        elif credit_score >= 700:
            return "low", 0.2
        elif credit_score >= 650:
            return "medium", 0.4
        elif credit_score >= 600:
            return "medium", 0.6
        elif credit_score >= 550:
            return "high", 0.8
        else:
            return "high", 1.0

    def assess_credit_risk_details(self, credit_record: CreditRecord) -> dict:
        """Assess credit risk based on credit record details.

        Args:
            credit_record: The applicant's credit record

        Returns:
            Dictionary with credit risk analysis
        """
        risk_factors = []
        risk_score_contribution = 0.0

        # Delinquencies
        if credit_record.delinquencies_last_24_months > 0:
            risk_factors.append(
                f"Recent delinquencies: {credit_record.delinquencies_last_24_months} "
                "in last 24 months"
            )
            risk_score_contribution += min(
                credit_record.delinquencies_last_24_months * 0.15, 0.3
            )

        # Public records
        if credit_record.public_records > 0:
            risk_factors.append(
                f"Public records found: {credit_record.public_records} records"
            )
            risk_score_contribution += min(credit_record.public_records * 0.2, 0.25)

        # Credit history length
        if credit_record.years_of_credit_history < 2:
            risk_factors.append("Limited credit history: Less than 2 years")
            risk_score_contribution += 0.1

        # Number of accounts
        if credit_record.number_of_accounts < 2:
            risk_factors.append("Limited credit accounts: Less than 2 accounts")
            risk_score_contribution += 0.05

        return {
            "credit_score_risk_level": self.map_credit_score_to_risk(
                credit_record.credit_score
            )[0],
            "risk_factors": risk_factors,
            "risk_contribution": risk_score_contribution,
        }

    def assess_loan_amount_risk(
        self,
        loan_amount: float,
        annual_income: float,
        current_debt: float,
        loan_term_months: int,
    ) -> tuple[str, float, List[str]]:
        """Assess risk based on loan amount relative to applicant profile.

        Args:
            loan_amount: The requested loan amount
            annual_income: Applicant's annual income
            current_debt: Current debt obligations
            loan_term_months: Loan term in months

        Returns:
            Tuple of (risk_level, risk_factor, risk_factors_list)
        """
        risk_factors = []
        risk_score = 0.0

        # Loan-to-Income (LTI) ratio
        if annual_income > 0:
            lti_ratio = (loan_amount / annual_income) * 100
            if lti_ratio > 500:
                risk_factors.append(f"Very high Loan-to-Income ratio: {lti_ratio:.1f}%")
                risk_score += 0.4
            elif lti_ratio > 300:
                risk_factors.append(f"High Loan-to-Income ratio: {lti_ratio:.1f}%")
                risk_score += 0.25
            elif lti_ratio > 150:
                risk_factors.append(f"Moderate Loan-to-Income ratio: {lti_ratio:.1f}%")
                risk_score += 0.1

        # Debt-to-Loan ratio
        total_debt = current_debt + loan_amount
        if annual_income > 0:
            debt_ratio = (total_debt / annual_income) * 100
            if debt_ratio > 300:
                risk_factors.append(
                    f"Total debt exceeds 3x annual income: {debt_ratio:.1f}%"
                )
                risk_score += 0.2

        # Short loan term
        if loan_term_months < 12:
            risk_factors.append(f"Very short loan term: {loan_term_months} months")
            risk_score += 0.15

        # Determine risk level
        if risk_score >= 0.5:
            risk_level = "high"
        elif risk_score >= 0.2:
            risk_level = "medium"
        else:
            risk_level = "low"

        return risk_level, risk_score, risk_factors

    def detect_anomalies(self, application_data: dict) -> List[str]:
        """Detect anomalies in the loan application.

        Args:
            application_data: The complete application data

        Returns:
            List of detected anomalies
        """
        anomalies = []

        employment_info = application_data.get("employment_info", {})
        credit_record = application_data.get("credit_record", {})
        loan_details = application_data.get("loan_details", {})
        applicant_profile = application_data.get("applicant_profile", {})

        # Inconsistent income reporting
        annual_income = employment_info.get("annual_income", 0)
        monthly_income = employment_info.get("monthly_income")
        if monthly_income and annual_income > 0:
            expected_monthly = annual_income / 12
            if abs(monthly_income - expected_monthly) > expected_monthly * 0.2:
                anomalies.append(
                    f"Income mismatch: Monthly income {monthly_income} "
                    f"inconsistent with annual income {annual_income}"
                )

        # Recent employment change
        years_employed = employment_info.get("years_employed", 0)
        if years_employed < 0.5:
            anomalies.append("Recently employed: Less than 6 months on current job")

        # Recent credit inquiries implied by delinquencies spike
        delinquencies = credit_record.get("delinquencies_last_24_months", 0)
        if delinquencies > 3:
            anomalies.append(
                f"Multiple recent delinquencies: {delinquencies} "
                "in last 24 months may indicate financial stress"
            )

        # Unusual loan request
        loan_amount = loan_details.get("loan_amount", 0)
        loan_purpose = loan_details.get("loan_purpose", "").lower()
        if loan_amount > annual_income * 5 and "consolidation" not in loan_purpose:
            anomalies.append(
                f"Unusually large loan request: {loan_amount} "
                f"relative to income {annual_income}"
            )

        # Very short loan term with large amount
        loan_term = loan_details.get("loan_term_months", 0)
        if loan_amount > 0 and loan_term > 0:
            monthly_payment_estimate = loan_amount / loan_term
            if monthly_payment_estimate > annual_income / 12 * 0.5:
                anomalies.append(
                    f"High monthly payment relative to income: "
                    f"Estimated {monthly_payment_estimate:.2f}/month"
                )

        return anomalies

    def analyze_patterns_with_claude(
        self, application_data: dict, initial_analysis: dict
    ) -> dict:
        """Use Claude to analyze complex patterns and synthesize risk insights.

        Args:
            application_data: The complete application data
            initial_analysis: Initial risk analysis results

        Returns:
            Dictionary with Claude's pattern analysis and insights
        """
        try:
            system_prompt = """You are a financial risk analysis expert evaluating loan applications.
Your task is to analyze the provided financial data and risk indicators to identify patterns and provide
synthesis of overall risk. Focus on:
1. Interconnected risk factors (how risks compound)
2. Patterns in the applicant's financial behavior
3. Mitigating factors that reduce risk
4. Hidden risks not captured in standard metrics
5. Overall risk assessment and key recommendations

Provide concise, actionable insights in 2-3 sentences."""

            analysis_text = f"""
Applicant Financial Profile:
- Annual Income: ${application_data.get('employment_info', {}).get('annual_income', 0):,.2f}
- Current Debt: ${application_data.get('credit_record', {}).get('current_debt', 0):,.2f}
- Credit Score: {application_data.get('credit_record', {}).get('credit_score', 0)}
- Years of Credit History: {application_data.get('credit_record', {}).get('years_of_credit_history', 0):.1f}
- Years Employed: {application_data.get('employment_info', {}).get('years_employed', 0):.1f}

Loan Request:
- Amount: ${application_data.get('loan_details', {}).get('loan_amount', 0):,.2f}
- Purpose: {application_data.get('loan_details', {}).get('loan_purpose', 'Unknown')}
- Term: {application_data.get('loan_details', {}).get('loan_term_months', 0)} months

Initial Risk Analysis:
- DTI Ratio: {initial_analysis.get('dti_ratio', 0):.2f}%
- DTI Risk Level: {initial_analysis.get('dti_risk_level', 'unknown')}
- Credit Risk Level: {initial_analysis.get('credit_risk_level', 'unknown')}
- Loan Amount Risk: {initial_analysis.get('loan_amount_risk_level', 'unknown')}
- Detected Anomalies: {', '.join(initial_analysis.get('anomalies', [])) if initial_analysis.get('anomalies') else 'None'}

Please analyze these patterns and provide:
1. Key risk drivers and interactions
2. Positive factors supporting loan approval
3. Overall risk synthesis
4. Recommendations for loan officers"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": analysis_text,
                    }
                ]
            )

            claude_analysis = response.content[0].text

            logger.info(
                f"Claude pattern analysis completed",
                extra={"analysis_length": len(claude_analysis)},
            )

            return {
                "claude_analysis": claude_analysis,
                "analysis_completed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Error during Claude analysis: {str(e)}",
                extra={"error_type": type(e).__name__},
            )
            return {
                "claude_analysis": "Pattern analysis unavailable",
                "error": str(e),
            }

    def calculate_overall_risk_score(
        self,
        dti_risk_level: str,
        credit_risk_level: str,
        loan_amount_risk_level: str,
        credit_risk_contribution: float,
        loan_amount_risk_contribution: float,
        anomalies_count: int,
    ) -> float:
        """Calculate overall risk score (0-100, higher = riskier).

        Args:
            dti_risk_level: DTI risk level ('low', 'medium', 'high')
            credit_risk_level: Credit risk level ('low', 'medium', 'high')
            loan_amount_risk_level: Loan amount risk level ('low', 'medium', 'high')
            credit_risk_contribution: Risk contribution from credit (0-1)
            loan_amount_risk_contribution: Risk contribution from loan amount (0-1)
            anomalies_count: Number of detected anomalies

        Returns:
            Overall risk score (0-100)
        """
        score = 0.0

        # DTI risk (30% weight)
        dti_scores = {"low": 10, "medium": 50, "high": 90}
        score += dti_scores.get(dti_risk_level, 50) * 0.3

        # Credit risk (30% weight)
        credit_scores = {"low": 10, "medium": 50, "high": 90}
        base_credit_score = credit_scores.get(credit_risk_level, 50)
        adjusted_credit_score = base_credit_score + (credit_risk_contribution * 20)
        score += min(adjusted_credit_score, 100) * 0.3

        # Loan amount risk (25% weight)
        loan_scores = {"low": 15, "medium": 50, "high": 85}
        base_loan_score = loan_scores.get(loan_amount_risk_level, 50)
        adjusted_loan_score = base_loan_score + (loan_amount_risk_contribution * 20)
        score += min(adjusted_loan_score, 100) * 0.25

        # Anomalies (15% weight)
        anomaly_score = min(anomalies_count * 15, 100)
        score += anomaly_score * 0.15

        return min(max(score, 0), 100)

    def analyze(self, application: LoanApplicationRequest) -> Dict[str, Any]:
        """Perform comprehensive financial risk analysis.

        Args:
            application: The loan application request

        Returns:
            Dictionary containing complete risk analysis
        """
        logger.info(
            "Starting financial risk analysis",
            extra={"loan_amount": application.loan_details.loan_amount},
        )

        try:
            # Extract application data
            app_data = {
                "employment_info": application.employment_info.model_dump(),
                "credit_record": application.credit_record.model_dump(),
                "loan_details": application.loan_details.model_dump(),
                "applicant_profile": application.applicant_profile.model_dump(),
            }

            # 1. Calculate DTI ratio
            current_debt = application.credit_record.current_debt
            monthly_loan_payment = (
                application.loan_details.loan_amount
                / application.loan_details.loan_term_months
            )
            total_monthly_debt = (current_debt / 12) + monthly_loan_payment

            dti_ratio = self.calculate_dti_ratio(
                application.employment_info.annual_income, total_monthly_debt
            )
            dti_risk_level = self.assess_dti_risk(dti_ratio)

            # 2. Map credit score to risk
            credit_risk_level, credit_risk_factor = self.map_credit_score_to_risk(
                application.credit_record.credit_score
            )

            # 3. Get detailed credit risk assessment
            credit_risk_details = self.assess_credit_risk_details(
                application.credit_record
            )

            # 4. Assess loan amount risk
            (
                loan_amount_risk_level,
                loan_amount_risk_score,
                loan_amount_risk_factors,
            ) = self.assess_loan_amount_risk(
                application.loan_details.loan_amount,
                application.employment_info.annual_income,
                application.credit_record.current_debt,
                application.loan_details.loan_term_months,
            )

            # 5. Detect anomalies
            anomalies = self.detect_anomalies(app_data)

            # Build initial analysis for Claude
            initial_analysis = {
                "dti_ratio": dti_ratio,
                "dti_risk_level": dti_risk_level,
                "credit_risk_level": credit_risk_level,
                "credit_risk_contribution": credit_risk_factor,
                "loan_amount_risk_level": loan_amount_risk_level,
                "loan_amount_risk_contribution": loan_amount_risk_score,
                "anomalies": anomalies,
                "credit_risk_details": credit_risk_details,
                "loan_amount_risk_factors": loan_amount_risk_factors,
            }

            # 6. Use Claude for pattern analysis
            claude_results = self.analyze_patterns_with_claude(
                app_data, initial_analysis
            )

            # 7. Calculate overall risk score
            overall_risk_score = self.calculate_overall_risk_score(
                dti_risk_level=dti_risk_level,
                credit_risk_level=credit_risk_level,
                loan_amount_risk_level=loan_amount_risk_level,
                credit_risk_contribution=credit_risk_factor,
                loan_amount_risk_contribution=loan_amount_risk_score,
                anomalies_count=len(anomalies),
            )

            # Compile all risk factors
            risk_factors = (
                credit_risk_details.get("risk_factors", [])
                + loan_amount_risk_factors
                + anomalies
            )

            result = {
                "risk_score": overall_risk_score,
                "dti_ratio": dti_ratio,
                "dti_risk_level": dti_risk_level,
                "credit_risk": credit_risk_level,
                "credit_score_value": application.credit_record.credit_score,
                "loan_amount_risk": loan_amount_risk_level,
                "anomalies": anomalies,
                "risk_factors": risk_factors,
                "positive_factors": [],
                "claude_analysis": claude_results.get("claude_analysis", ""),
                "analyzed_at": datetime.utcnow().isoformat(),
            }

            # Extract positive factors
            positive_factors = []
            if dti_risk_level == "low":
                positive_factors.append("Good debt-to-income ratio")
            if credit_risk_level == "low":
                positive_factors.append("Strong credit profile")
            if application.employment_info.years_employed >= 2:
                positive_factors.append("Stable employment history")
            if application.credit_record.years_of_credit_history >= 5:
                positive_factors.append("Established credit history")
            if application.credit_record.delinquencies_last_24_months == 0:
                positive_factors.append("No recent delinquencies")

            result["positive_factors"] = positive_factors

            logger.info(
                "Financial risk analysis completed",
                extra={
                    "risk_score": overall_risk_score,
                    "dti_ratio": dti_ratio,
                    "anomalies_count": len(anomalies),
                },
            )

            return result

        except Exception as e:
            logger.error(
                f"Error during risk analysis: {str(e)}",
                extra={"error_type": type(e).__name__},
            )
            raise


# Singleton instance
_risk_agent: Optional[FinancialRiskAnalysisAgent] = None


def get_risk_agent() -> FinancialRiskAnalysisAgent:
    """Get or create the risk analysis agent singleton."""
    global _risk_agent
    if _risk_agent is None:
        _risk_agent = FinancialRiskAnalysisAgent()
    return _risk_agent
