"""MCP Server for Decision Synthesis - Exposes loan decision synthesis tools."""

import json
from typing import Any, Optional

from fastmcp import Server
from pydantic import BaseModel

from agents.decision_agent import get_decision_agent
from models.schemas import LoanApplicationRequest
from shared.logger import get_logger

logger = get_logger("decision_synthesis_server")

# Initialize MCP server
server = Server("DecisionSynthesis")


class DecisionSynthesisRequest(BaseModel):
    """Request model for decision synthesis."""

    application_data: dict
    applicant_analysis: dict
    risk_analysis: dict


@server.call_tool()
async def synthesize_decision(
    application_data: dict,
    applicant_analysis: dict,
    risk_analysis: dict,
) -> dict:
    """Synthesize a loan decision from analysis results.

    Args:
        application_data: Complete loan application data
        applicant_analysis: Result from ApplicantProfileAgent
        risk_analysis: Result from FinancialRiskAnalysisAgent

    Returns:
        Loan decision with classification and reasoning
    """
    try:
        logger.info("Synthesizing decision from analysis results")

        # Reconstruct LoanApplicationRequest from dict
        application = LoanApplicationRequest(**application_data)

        agent = get_decision_agent()
        decision_result = agent.decide(
            application=application,
            applicant_analysis=applicant_analysis,
            risk_analysis=risk_analysis,
        )

        return {
            "success": True,
            "decision": decision_result,
            "message": f"Decision synthesized: {decision_result['classification_value']}",
        }
    except Exception as e:
        logger.error(f"Error synthesizing decision: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def calculate_confidence_score(
    applicant_analysis: dict,
    risk_analysis: dict,
    risk_score: float,
) -> dict:
    """Calculate confidence score for the decision.

    Args:
        applicant_analysis: Applicant profile analysis results
        risk_analysis: Financial risk analysis results
        risk_score: Overall risk score (0-100)

    Returns:
        Confidence score (0-1) and explanation
    """
    try:
        agent = get_decision_agent()
        confidence = agent._calculate_confidence(
            applicant_analysis, risk_analysis, risk_score
        )

        explanation = f"Confidence based on profile completeness {applicant_analysis.get('profile_completeness', 0):.0f}%, "
        explanation += f"consistency between risk metrics, and extremeness of risk score {risk_score:.0f}/100."

        return {
            "success": True,
            "confidence_score": confidence,
            "explanation": explanation,
            "message": f"Confidence score calculated: {confidence:.2f}",
        }
    except Exception as e:
        logger.error(f"Error calculating confidence: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def extract_decision_factors(
    applicant_analysis: dict,
    risk_analysis: dict,
) -> dict:
    """Extract key risk and positive factors influencing the decision.

    Args:
        applicant_analysis: Applicant profile analysis
        risk_analysis: Financial risk analysis

    Returns:
        Lists of risk factors and positive factors
    """
    try:
        agent = get_decision_agent()
        risk_factors = agent._extract_risk_factors(applicant_analysis, risk_analysis)
        positive_factors = risk_analysis.get("positive_factors", [])

        return {
            "success": True,
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "risk_factor_count": len(risk_factors),
            "positive_factor_count": len(positive_factors),
            "message": f"Extracted {len(risk_factors)} risk factors and {len(positive_factors)} positive factors",
        }
    except Exception as e:
        logger.error(f"Error extracting factors: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def determine_conditions(
    classification: str,
    risk_factors: list,
    risk_score: float,
) -> dict:
    """Determine loan conditions and requirements based on decision.

    Args:
        classification: Decision classification (approved, rejected, manual_review)
        risk_factors: List of identified risk factors
        risk_score: Overall risk score (0-100)

    Returns:
        List of conditions and requirements
    """
    try:
        from models.schemas import DecisionClassification

        agent = get_decision_agent()
        decision_classification = DecisionClassification(classification)

        conditions = agent._extract_conditions(
            decision_classification, risk_factors, risk_score
        )

        return {
            "success": True,
            "conditions": conditions,
            "condition_count": len(conditions),
            "message": f"Determined {len(conditions)} conditions for {classification} decision",
        }
    except Exception as e:
        logger.error(f"Error determining conditions: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def calculate_recommended_rate(
    risk_score: float,
    base_interest_rate: Optional[float] = None,
) -> dict:
    """Calculate recommended interest rate based on risk score.

    Args:
        risk_score: Overall risk score (0-100)
        base_interest_rate: Base interest rate (optional)

    Returns:
        Recommended interest rate and pricing explanation
    """
    try:
        agent = get_decision_agent()
        recommended_rate = agent._calculate_interest_rate(risk_score, base_interest_rate)

        if base_interest_rate is None:
            explanation = "Interest rate calculation requires a base rate."
        else:
            rate_adjustment = recommended_rate - base_interest_rate if recommended_rate else 0
            explanation = (
                f"Based on risk score {risk_score:.0f}/100, "
                f"recommended rate is base + {rate_adjustment:.1f}% = {recommended_rate:.2f}%"
            )

        return {
            "success": True,
            "recommended_rate": recommended_rate,
            "base_rate": base_interest_rate,
            "explanation": explanation,
            "message": "Interest rate calculated",
        }
    except Exception as e:
        logger.error(f"Error calculating rate: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def get_decision_rules() -> dict:
    """Get all decision rules and thresholds used by the decision agent.

    Returns:
        Dictionary with all decision thresholds and rules
    """
    try:
        agent = get_decision_agent()

        rules = {
            "risk_thresholds": {
                "approve": agent.RISK_THRESHOLD_APPROVE,
                "manual_review": agent.RISK_THRESHOLD_REVIEW,
                "reject": agent.RISK_THRESHOLD_REJECT,
            },
            "confidence_bounds": {
                "minimum": agent.MIN_CONFIDENCE,
                "maximum": agent.MAX_CONFIDENCE,
            },
            "decision_logic": {
                "approved": f"Risk score < {agent.RISK_THRESHOLD_APPROVE}",
                "manual_review": f"Risk score between {agent.RISK_THRESHOLD_APPROVE}-{agent.RISK_THRESHOLD_REVIEW}",
                "rejected": f"Risk score >= {agent.RISK_THRESHOLD_REVIEW}",
            },
        }

        return {
            "success": True,
            "rules": rules,
            "message": "Decision rules retrieved",
        }
    except Exception as e:
        logger.error(f"Error retrieving rules: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def health_check() -> dict:
    """Health check for the Decision Synthesis MCP server.

    Returns:
        Server status information
    """
    try:
        agent = get_decision_agent()
        logger.info("Decision Synthesis MCP server is healthy")
        return {
            "success": True,
            "status": "healthy",
            "server": "DecisionSynthesis",
            "agent_initialized": True,
            "message": "Decision Synthesis MCP server is operational",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
        }
