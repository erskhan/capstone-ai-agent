"""Service for retrieving and formatting decision details."""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from shared.logger import get_logger
from shared.exceptions import AgentException

logger = get_logger("decision_service")


class DecisionService:
    """Manages loan decision retrieval and formatting."""

    @staticmethod
    def get_decision_details(
        db: Session,
        application_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get full decision details for an application.

        Args:
            db: Database session
            application_id: Application ID

        Returns:
            Dictionary with decision details or None
        """
        try:
            from database.models import WorkflowExecutionModel

            execution = (
                db.query(WorkflowExecutionModel)
                .filter_by(application_id=application_id)
                .first()
            )

            if not execution or not execution.decision_result:
                logger.debug(f"No decision found for {application_id}")
                return None

            decision = execution.decision_result

            return {
                "application_id": application_id,
                "classification": decision.get("classification_value"),
                "confidence_score": decision.get("confidence_score", 0),
                "risk_score": decision.get("risk_score", 0),
                "reasoning": decision.get("reasoning", ""),
                "decision_factors": {
                    "positive_factors": decision.get("positive_factors", []),
                    "risk_factors": decision.get("risk_factors", []),
                },
                "recommended_rate": decision.get("recommended_rate"),
                "approved_loan_amount": decision.get("approved_loan_amount"),
                "conditions": decision.get("conditions", []),
                "compliance_notes": execution.decision_result.get("compliance_notes"),
            }

        except Exception as e:
            logger.error(
                f"Error retrieving decision details: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def get_decision_summary(
        db: Session,
        application_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get brief decision summary.

        Args:
            db: Database session
            application_id: Application ID

        Returns:
            Dictionary with decision summary
        """
        try:
            from database.models import WorkflowExecutionModel

            execution = (
                db.query(WorkflowExecutionModel)
                .filter_by(application_id=application_id)
                .first()
            )

            if not execution:
                return None

            decision = execution.decision_result or {}

            return {
                "application_id": application_id,
                "classification": decision.get("classification_value", "unknown"),
                "confidence_score": decision.get("confidence_score", 0),
                "workflow_state": execution.workflow_state,
                "decision_made_at": execution.completed_at.isoformat()
                if execution.completed_at
                else None,
            }

        except Exception as e:
            logger.error(
                f"Error retrieving decision summary: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def format_decision_letter(
        db: Session,
        application_id: str,
        applicant_name: str,
        include_reasoning: bool = True,
    ) -> Optional[str]:
        """Format decision as a letter.

        Args:
            db: Database session
            application_id: Application ID
            applicant_name: Applicant full name
            include_reasoning: Whether to include detailed reasoning

        Returns:
            Formatted decision letter or None
        """
        try:
            decision = DecisionService.get_decision_details(db, application_id)

            if not decision:
                return None

            classification = decision["classification"]
            reasoning = decision["reasoning"] if include_reasoning else ""
            approved_amount = decision.get("approved_loan_amount")
            recommended_rate = decision.get("recommended_rate")
            conditions = decision.get("conditions", [])

            if classification == "approved":
                letter = f"""
LOAN APPROVAL LETTER
====================

Dear {applicant_name},

We are pleased to inform you that your loan application has been APPROVED!

APPROVAL DETAILS:
- Application ID: {application_id}
- Approved Loan Amount: ${approved_amount:,.2f}
- Recommended Interest Rate: {recommended_rate:.2f}%
- Loan Term: To be discussed with your loan officer

NEXT STEPS:
1. A loan officer will contact you within 1 business day
2. We will finalize the loan documentation
3. Funding will be processed within 5-7 business days

LOAN CONDITIONS:
{chr(10).join([f'  - {condition}' for condition in conditions]) if conditions else '  - No additional conditions'}

{'DECISION REASONING:' + chr(10) + reasoning if include_reasoning else ''}

If you have any questions, please contact us at:
Phone: 1-800-LOAN-APP
Email: support@loanapp.com

Thank you for choosing us!

Best regards,
Loan Approval System
            """.strip()

            elif classification == "rejected":
                letter = f"""
LOAN APPLICATION DECISION LETTER
=================================

Dear {applicant_name},

Thank you for your loan application. After careful review, we are unable to
approve your application at this time.

APPLICATION ID: {application_id}

REASON FOR DECISION:
{reasoning if include_reasoning else 'Your creditworthiness profile did not meet our lending criteria.'}

YOUR RIGHTS:
You have the right to appeal this decision within 30 days. Please see the attached
adverse action notice for complete information about your appeal rights and the
reasons for this decision.

TO APPEAL:
- Email: support@loanapp.com with subject "APPEAL REQUEST"
- Phone: 1-800-LOAN-APP (Mon-Fri, 9 AM - 5 PM EST)
- Online: Visit www.loanapp.com/appeal

CREDIT REPORT:
You are entitled to a free copy of the credit report used in this decision
within 60 days of receiving this notice. Visit www.annualcreditreport.com

We encourage you to:
1. Review your credit report for accuracy
2. Consider improving your credit profile
3. Reapply after 6 months if your situation improves

For questions, contact us at:
Phone: 1-800-LOAN-APP
Email: support@loanapp.com

Sincerely,
Loan Approval System
Compliance Division
            """.strip()

            else:  # manual_review
                letter = f"""
LOAN APPLICATION STATUS LETTER
===============================

Dear {applicant_name},

Your loan application is currently under manual review by our lending team.

APPLICATION ID: {application_id}

REVIEW STATUS: Under Manual Review
Expected Decision: Within 3-5 business days
Your application has been assigned to a senior loan officer for comprehensive review.

{'NOTES:' + chr(10) + reasoning if include_reasoning else ''}

NEXT STEPS:
- A loan officer may contact you with questions or requests for additional information
- You will receive a notification once a decision has been made
- You can check your status at any time by visiting our website

You will be notified of the final decision via:
- Email to your registered address
- Phone call if requested
- In-app notification

If you have any urgent questions, please contact us at:
Phone: 1-800-LOAN-APP
Email: support@loanapp.com

Thank you for your patience!

Sincerely,
Loan Approval System
            """.strip()

            return letter

        except Exception as e:
            logger.error(
                f"Error formatting decision letter: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def get_comparative_analysis(
        db: Session,
        application_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get comparative analysis of decision vs applicant profile.

        Args:
            db: Database session
            application_id: Application ID

        Returns:
            Dictionary with comparative analysis
        """
        try:
            from database.models import WorkflowExecutionModel

            execution = (
                db.query(WorkflowExecutionModel)
                .filter_by(application_id=application_id)
                .first()
            )

            if not execution:
                return None

            applicant_analysis = execution.applicant_result or {}
            risk_analysis = execution.risk_analysis or {}
            decision = execution.decision_result or {}

            return {
                "application_id": application_id,
                "applicant_profile": {
                    "income_stability": applicant_analysis.get("income_stability_level"),
                    "employment_risk": applicant_analysis.get("employment_risk_level"),
                    "credit_summary": applicant_analysis.get("credit_summary"),
                    "data_completeness": applicant_analysis.get("data_completeness_percentage"),
                },
                "risk_assessment": {
                    "overall_risk_score": risk_analysis.get("risk_score"),
                    "dti_ratio": risk_analysis.get("debt_to_income_ratio"),
                    "credit_risk": risk_analysis.get("credit_risk_level"),
                    "anomalies_detected": len(risk_analysis.get("anomalies", [])),
                },
                "decision_outcome": {
                    "classification": decision.get("classification_value"),
                    "confidence": decision.get("confidence_score"),
                    "key_factors": decision.get("decision_factors", {}),
                },
                "alignment": {
                    "risk_matches_decision": DecisionService._analyze_alignment(
                        risk_analysis.get("risk_score"),
                        decision.get("classification_value"),
                    ),
                },
            }

        except Exception as e:
            logger.error(
                f"Error generating comparative analysis: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def _analyze_alignment(risk_score: float, classification: str) -> Dict[str, Any]:
        """Analyze alignment between risk score and decision."""
        if risk_score is None or classification is None:
            return {"aligned": None, "explanation": "Missing data"}

        if classification == "approved":
            aligned = risk_score < 35
            explanation = (
                f"Approved with risk score {risk_score:.0f} - consistent"
                if aligned
                else f"Approved with higher risk score {risk_score:.0f} - may indicate override"
            )
        elif classification == "rejected":
            aligned = risk_score > 80
            explanation = (
                f"Rejected with high risk score {risk_score:.0f} - consistent"
                if aligned
                else f"Rejected with lower risk score {risk_score:.0f} - may indicate override"
            )
        else:  # manual_review
            aligned = 35 <= risk_score <= 80
            explanation = (
                f"Manual review with risk score {risk_score:.0f} - consistent"
                if aligned
                else f"Manual review with risk score {risk_score:.0f} - may indicate threshold issue"
            )

        return {"aligned": aligned, "explanation": explanation}
