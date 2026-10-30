"""MCP server for Notification System providing notification management tools."""

from typing import Any, Dict, Optional
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP, Session

from agents.notification_agent import NotificationAgent, NotificationTemplate
from shared.logger import get_logger

logger = get_logger("notification_system_server")

# Initialize MCP server
server = FastMCP("NotificationSystem")

# Initialize notification agent
notification_agent = NotificationAgent()


@server.call_tool()
async def queue_decision_notification(
    application_id: str,
    applicant_name: str,
    applicant_email: str,
    applicant_phone: Optional[str],
    classification: str,
    risk_score: float,
    approved_amount: Optional[float] = None,
    recommended_rate: Optional[float] = None,
    reasoning: Optional[str] = None,
) -> Dict[str, Any]:
    """Queue a decision notification for delivery.

    Args:
        application_id: Unique application ID
        applicant_name: Full name of applicant
        applicant_email: Email address
        applicant_phone: Phone number (optional)
        classification: Decision classification (approved/rejected/manual_review)
        risk_score: Risk assessment score
        approved_amount: Approved loan amount if applicable
        recommended_rate: Interest rate recommendation if applicable
        reasoning: Decision reasoning for notification

    Returns:
        Dictionary with notification queue status
    """
    try:
        logger.debug(
            f"MCP tool called: queue_decision_notification for {application_id}",
            extra={"classification": classification},
        )

        result = notification_agent.queue_decision_notification(
            application_id=application_id,
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            applicant_phone=applicant_phone,
            classification=classification,
            risk_score=risk_score,
            approved_amount=approved_amount,
            recommended_rate=recommended_rate,
            reasoning=reasoning,
        )

        return {
            "success": True,
            "data": result,
            "message": f"Queued {result['notifications_queued']} notifications",
        }

    except Exception as e:
        logger.error(
            f"Error queuing notification: {str(e)}",
            exc_info=True,
        )
        return {"success": False, "error": str(e), "application_id": application_id}


@server.call_tool()
async def queue_appeal_notification(
    application_id: str,
    applicant_name: str,
    applicant_email: str,
    appeal_status: str,
    appeal_decision: Optional[str] = None,
    original_decision: Optional[str] = None,
    new_decision: Optional[str] = None,
) -> Dict[str, Any]:
    """Queue an appeal-related notification.

    Args:
        application_id: Application ID
        applicant_name: Applicant name
        applicant_email: Email address
        appeal_status: Status of appeal (received/approved/rejected/pending)
        appeal_decision: New decision if appeal completed
        original_decision: Original decision classification
        new_decision: New decision classification after appeal

    Returns:
        Dictionary with appeal notification details
    """
    try:
        logger.debug(
            f"MCP tool called: queue_appeal_notification for {application_id}",
            extra={"appeal_status": appeal_status},
        )

        result = notification_agent.queue_appeal_notification(
            application_id=application_id,
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            appeal_status=appeal_status,
            appeal_decision=appeal_decision,
            original_decision=original_decision,
            new_decision=new_decision,
        )

        return {
            "success": True,
            "data": result,
            "message": f"Appeal notification queued with status: {appeal_status}",
        }

    except Exception as e:
        logger.error(
            f"Error queuing appeal notification: {str(e)}",
            exc_info=True,
        )
        return {"success": False, "error": str(e), "application_id": application_id}


@server.call_tool()
async def get_notification_templates() -> Dict[str, Any]:
    """Get list of available notification templates.

    Returns:
        Dictionary with available templates and descriptions
    """
    try:
        logger.debug("MCP tool called: get_notification_templates")

        templates = {
            "loan_approved": {
                "description": "Notification for approved loan applications",
                "channels": ["email", "sms", "in_app"],
                "subject": "Loan Application Approved",
                "includes": ["approved_amount", "interest_rate", "next_steps"],
            },
            "loan_rejected": {
                "description": "Notification for rejected loan applications",
                "channels": ["email", "sms", "in_app"],
                "subject": "Loan Application Decision - Appeal Available",
                "includes": ["appeal_rights", "appeal_deadline", "contact_info"],
            },
            "loan_under_review": {
                "description": "Notification for applications under review",
                "channels": ["email", "in_app"],
                "subject": "Loan Application Status Update",
                "includes": ["review_timeline", "next_steps", "status_check_link"],
            },
            "appeal_received": {
                "description": "Confirmation that appeal has been received",
                "channels": ["email", "in_app"],
                "subject": "Appeal Received - Reference Number",
                "includes": ["reference_number", "review_timeline", "contact_info"],
            },
            "appeal_approved": {
                "description": "Notification that appeal was approved",
                "channels": ["email", "sms", "in_app"],
                "subject": "Appeal Approved - Your Loan Has Been Approved",
                "includes": ["new_decision", "next_steps", "loan_terms"],
            },
            "appeal_rejected": {
                "description": "Notification that appeal was not approved",
                "channels": ["email", "in_app"],
                "subject": "Appeal Review Complete",
                "includes": ["review_status", "next_steps", "contact_info"],
            },
        }

        return {
            "success": True,
            "data": {
                "templates": templates,
                "total": len(templates),
                "supported_channels": ["email", "sms", "in_app"],
            },
            "message": f"Available {len(templates)} notification templates",
        }

    except Exception as e:
        logger.error(
            f"Error retrieving templates: {str(e)}",
            exc_info=True,
        )
        return {"success": False, "error": str(e)}


@server.call_tool()
async def validate_notification_recipients(
    email: Optional[str] = None,
    phone: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate notification recipient contact information.

    Args:
        email: Email address to validate
        phone: Phone number to validate

    Returns:
        Dictionary with validation results
    """
    try:
        logger.debug(
            "MCP tool called: validate_notification_recipients",
            extra={"has_email": email is not None, "has_phone": phone is not None},
        )

        results = {}

        # Validate email
        if email:
            email_valid = "@" in email and "." in email.split("@")[1]
            results["email"] = {
                "valid": email_valid,
                "value": email if email_valid else None,
                "error": None if email_valid else "Invalid email format",
            }

        # Validate phone
        if phone:
            # Remove non-digit characters
            phone_digits = "".join(filter(str.isdigit, phone))
            phone_valid = len(phone_digits) >= 10
            results["phone"] = {
                "valid": phone_valid,
                "value": phone if phone_valid else None,
                "error": None
                if phone_valid
                else f"Invalid phone format (need at least 10 digits, got {len(phone_digits)})",
            }

        return {
            "success": True,
            "data": results,
            "all_valid": all(r.get("valid", False) for r in results.values()),
            "message": "Validation complete",
        }

    except Exception as e:
        logger.error(
            f"Error validating recipients: {str(e)}",
            exc_info=True,
        )
        return {"success": False, "error": str(e)}


@server.call_tool()
async def get_notification_status(application_id: str) -> Dict[str, Any]:
    """Get notification delivery status for an application.

    Args:
        application_id: Application ID to check

    Returns:
        Dictionary with notification status
    """
    try:
        logger.debug(
            f"MCP tool called: get_notification_status for {application_id}",
        )

        # This would query a database in production
        # For now, return a template response
        status = {
            "application_id": application_id,
            "notifications": [
                {
                    "id": f"notif-{application_id}-001",
                    "channel": "email",
                    "status": "queued",
                    "queued_at": datetime.utcnow().isoformat(),
                    "delivery_attempts": 0,
                    "next_retry": None,
                },
                {
                    "id": f"notif-{application_id}-002",
                    "channel": "in_app",
                    "status": "queued",
                    "queued_at": datetime.utcnow().isoformat(),
                    "delivery_attempts": 0,
                    "next_retry": None,
                },
            ],
            "summary": {
                "total": 2,
                "queued": 2,
                "delivered": 0,
                "failed": 0,
                "last_updated": datetime.utcnow().isoformat(),
            },
        }

        return {
            "success": True,
            "data": status,
            "message": "Notification status retrieved",
        }

    except Exception as e:
        logger.error(
            f"Error getting notification status: {str(e)}",
            exc_info=True,
        )
        return {"success": False, "error": str(e), "application_id": application_id}


@server.call_tool()
async def resend_notification(
    application_id: str,
    notification_id: str,
) -> Dict[str, Any]:
    """Resend a notification that failed to deliver.

    Args:
        application_id: Application ID
        notification_id: Notification ID to resend

    Returns:
        Dictionary with resend status
    """
    try:
        logger.debug(
            f"MCP tool called: resend_notification for {application_id}",
            extra={"notification_id": notification_id},
        )

        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "notification_id": notification_id,
                "status": "queued_for_resend",
                "resend_queued_at": datetime.utcnow().isoformat(),
                "retry_attempt": 1,
                "max_retries": 3,
            },
            "message": "Notification queued for resend",
        }

    except Exception as e:
        logger.error(
            f"Error resending notification: {str(e)}",
            exc_info=True,
        )
        return {"success": False, "error": str(e)}


@server.call_tool()
async def health_check() -> Dict[str, Any]:
    """Health check for notification system.

    Returns:
        Dictionary with system status
    """
    try:
        logger.debug("MCP tool called: health_check")

        return {
            "success": True,
            "data": {
                "service": "NotificationSystem",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "capabilities": [
                    "queue_decision_notification",
                    "queue_appeal_notification",
                    "get_notification_templates",
                    "validate_notification_recipients",
                    "get_notification_status",
                    "resend_notification",
                ],
            },
            "message": "Notification system is operational",
        }

    except Exception as e:
        logger.error(
            f"Health check failed: {str(e)}",
            exc_info=True,
        )
        return {
            "success": False,
            "error": str(e),
            "data": {"service": "NotificationSystem", "status": "unhealthy"},
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server, host="127.0.0.1", port=3005)
