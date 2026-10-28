"""MCP server for applicant database operations."""

from typing import Any

from shared.logger import get_logger

logger = get_logger("applicant_db_server")


class ApplicantDBServer:
    """MCP server for applicant profile data access."""

    def __init__(self):
        """Initialize the applicant database server."""
        logger.info("ApplicantDB server initialized")

    async def validate_applicant(self, applicant_data: dict) -> dict:
        """Validate applicant information."""
        logger.info(f"Validating applicant: {applicant_data.get('email')}")

        errors = []

        if not applicant_data.get("first_name"):
            errors.append("First name is required")
        if not applicant_data.get("last_name"):
            errors.append("Last name is required")
        if not applicant_data.get("email"):
            errors.append("Email is required")
        if not applicant_data.get("ssn"):
            errors.append("SSN is required")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "applicant_id": applicant_data.get("ssn"),
        }

    async def calculate_income_stability(self, employment_data: dict) -> dict:
        """Calculate income stability score."""
        logger.info(f"Calculating income stability for {employment_data.get('job_title')}")

        years_employed = employment_data.get("years_employed", 0)

        if years_employed >= 5:
            stability_score = 0.9
        elif years_employed >= 2:
            stability_score = 0.7
        elif years_employed >= 1:
            stability_score = 0.5
        else:
            stability_score = 0.3

        return {
            "stability_score": stability_score,
            "years_employed": years_employed,
            "assessment": "Stable" if stability_score >= 0.7 else "Unstable",
        }

    async def get_tools(self) -> list:
        """Return available tools for this MCP server."""
        return [
            {
                "name": "validate_applicant",
                "description": "Validate applicant information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_data": {
                            "type": "object",
                            "description": "Applicant information to validate",
                        }
                    },
                    "required": ["applicant_data"],
                },
            },
            {
                "name": "calculate_income_stability",
                "description": "Calculate income stability score based on employment history",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "employment_data": {
                            "type": "object",
                            "description": "Employment information",
                        }
                    },
                    "required": ["employment_data"],
                },
            },
        ]
