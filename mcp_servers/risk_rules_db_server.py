"""MCP Server for Risk Rules Database - Exposes risk assessment tools."""

import json
import asyncio
from typing import Any, Optional
from datetime import datetime

from fastmcp import Server
from pydantic import BaseModel

from agents.risk_agent import get_risk_agent
from models.schemas import LoanApplicationRequest
from shared.logger import get_logger

logger = get_logger("risk_rules_db_server")

# Initialize MCP server
server = Server("RiskRulesDB")


class RiskAnalysisRequest(BaseModel):
    """Request model for risk analysis tool."""

    application_data: dict
    credit_score: int
    annual_income: float
    current_debt: float
    loan_amount: float
    loan_term_months: int


@server.call_tool()
async def calculate_dti_ratio(
    annual_income: float, monthly_debt_obligations: float
) -> dict:
    """Calculate Debt-to-Income (DTI) ratio.

    Args:
        annual_income: Applicant's annual income
        monthly_debt_obligations: Total monthly debt obligations

    Returns:
        DTI ratio and risk level assessment
    """
    try:
        agent = get_risk_agent()
        dti_ratio = agent.calculate_dti_ratio(annual_income, monthly_debt_obligations)
        dti_risk_level = agent.assess_dti_risk(dti_ratio)

        return {
            "success": True,
            "dti_ratio": dti_ratio,
            "dti_risk_level": dti_risk_level,
            "message": f"DTI calculated: {dti_ratio:.2f}% ({dti_risk_level} risk)",
        }
    except Exception as e:
        logger.error(f"Error calculating DTI: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def assess_credit_risk(credit_score: int) -> dict:
    """Assess credit score risk level.

    Args:
        credit_score: The applicant's credit score (300-850)

    Returns:
        Credit risk level and risk factor
    """
    try:
        agent = get_risk_agent()
        risk_level, risk_factor = agent.map_credit_score_to_risk(credit_score)

        return {
            "success": True,
            "credit_score": credit_score,
            "risk_level": risk_level,
            "risk_factor": risk_factor,
            "message": f"Credit score {credit_score} maps to {risk_level} risk",
        }
    except Exception as e:
        logger.error(f"Error assessing credit risk: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def detect_application_anomalies(
    annual_income: float,
    monthly_income: Optional[float],
    years_employed: float,
    current_debt: float,
    delinquencies_24_months: int,
    loan_amount: float,
    loan_purpose: str,
    loan_term_months: int,
) -> dict:
    """Detect anomalies in loan application.

    Args:
        annual_income: Applicant's annual income
        monthly_income: Reported monthly income (if provided)
        years_employed: Years in current employment
        current_debt: Current debt obligations
        delinquencies_24_months: Number of delinquencies in last 24 months
        loan_amount: Requested loan amount
        loan_purpose: Purpose of the loan
        loan_term_months: Loan term in months

    Returns:
        List of detected anomalies
    """
    try:
        agent = get_risk_agent()
        app_data = {
            "employment_info": {
                "annual_income": annual_income,
                "monthly_income": monthly_income,
                "years_employed": years_employed,
            },
            "credit_record": {
                "current_debt": current_debt,
                "delinquencies_last_24_months": delinquencies_24_months,
            },
            "loan_details": {
                "loan_amount": loan_amount,
                "loan_purpose": loan_purpose,
                "loan_term_months": loan_term_months,
            },
            "applicant_profile": {},
        }

        anomalies = agent.detect_anomalies(app_data)

        return {
            "success": True,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "message": f"Detected {len(anomalies)} anomalies",
        }
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def assess_loan_amount_risk(
    loan_amount: float,
    annual_income: float,
    current_debt: float,
    loan_term_months: int,
) -> dict:
    """Assess risk based on loan amount and applicant profile.

    Args:
        loan_amount: Requested loan amount
        annual_income: Applicant's annual income
        current_debt: Current debt obligations
        loan_term_months: Loan term in months

    Returns:
        Loan amount risk level and contributing factors
    """
    try:
        agent = get_risk_agent()
        risk_level, risk_score, risk_factors = agent.assess_loan_amount_risk(
            loan_amount, annual_income, current_debt, loan_term_months
        )

        return {
            "success": True,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "message": f"Loan amount risk: {risk_level}",
        }
    except Exception as e:
        logger.error(f"Error assessing loan amount risk: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def calculate_risk_score(
    dti_risk_level: str,
    credit_risk_level: str,
    loan_amount_risk_level: str,
    credit_risk_contribution: float,
    loan_amount_risk_contribution: float,
    anomalies_count: int,
) -> dict:
    """Calculate overall risk score (0-100).

    Args:
        dti_risk_level: DTI risk level (low/medium/high)
        credit_risk_level: Credit risk level (low/medium/high)
        loan_amount_risk_level: Loan amount risk level (low/medium/high)
        credit_risk_contribution: Credit risk contribution (0-1)
        loan_amount_risk_contribution: Loan amount risk contribution (0-1)
        anomalies_count: Number of detected anomalies

    Returns:
        Overall risk score (0-100)
    """
    try:
        agent = get_risk_agent()
        risk_score = agent.calculate_overall_risk_score(
            dti_risk_level=dti_risk_level,
            credit_risk_level=credit_risk_level,
            loan_amount_risk_level=loan_amount_risk_level,
            credit_risk_contribution=credit_risk_contribution,
            loan_amount_risk_contribution=loan_amount_risk_contribution,
            anomalies_count=anomalies_count,
        )

        risk_category = "high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low"

        return {
            "success": True,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "message": f"Overall risk score: {risk_score:.1f} ({risk_category} risk)",
        }
    except Exception as e:
        logger.error(f"Error calculating risk score: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def get_risk_rules() -> dict:
    """Get risk assessment rules and thresholds.

    Returns:
        Dictionary containing all risk assessment rules
    """
    try:
        rules = {
            "dti_thresholds": {
                "low": {"max": 36},
                "medium": {"min": 36, "max": 43},
                "high": {"min": 43},
            },
            "credit_score_thresholds": {
                "low_excellent": {"min": 750},
                "low_good": {"min": 700, "max": 749},
                "medium_fair": {"min": 650, "max": 699},
                "medium_poor": {"min": 600, "max": 649},
                "high_very_poor": {"max": 599},
            },
            "loan_to_income_limits": {
                "low": {"max": 150},
                "medium": {"min": 150, "max": 300},
                "high": {"min": 300, "max": 500},
                "extreme": {"min": 500},
            },
            "anomaly_factors": {
                "income_mismatch_threshold": 0.2,  # 20% variance
                "recent_employment_months": 6,
                "critical_delinquency_count": 3,
                "high_monthly_payment_ratio": 0.5,
            },
            "risk_score_weights": {
                "dti": 0.3,
                "credit": 0.3,
                "loan_amount": 0.25,
                "anomalies": 0.15,
            },
        }

        return {
            "success": True,
            "rules": rules,
            "last_updated": datetime.utcnow().isoformat(),
            "message": "Risk assessment rules retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Error retrieving risk rules: {str(e)}")
        return {"success": False, "error": str(e)}


@server.call_tool()
async def health_check() -> dict:
    """Health check for the Risk Rules DB server.

    Returns:
        Server health status
    """
    return {
        "status": "healthy",
        "service": "RiskRulesDB",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Risk Rules DB MCP Server")

    # Run the server
    async with server:
        logger.info("Risk Rules DB MCP Server is running")
        # Keep the server alive
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
