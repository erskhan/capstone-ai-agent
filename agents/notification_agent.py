"""Notification & Communication Agent for decision delivery."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from enum import Enum
import anthropic

from models.schemas import DecisionClassification
from shared.config import get_settings
from shared.logger import get_logger
from shared.exceptions import AgentException

logger = get_logger("notification_agent")


class NotificationChannel(str, Enum):
    """Supported notification channels."""

    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationTemplate(str, Enum):
    """Available notification templates."""

    APPROVED = "loan_approved"
    REJECTED = "loan_rejected"
    UNDER_REVIEW = "loan_under_review"
    APPEAL_RECEIVED = "appeal_received"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_REJECTED = "appeal_rejected"


class NotificationAgent:
    """Manages notification delivery, templates, and tracking."""

    def __init__(self):
        """Initialize notification agent with Anthropic client."""
        settings = get_settings()
        self.client = anthropic.Anthropic(
            api_key=settings.langsmith_api_key,
            base_url=settings.langsmith_base_url,
        )
        self.model = "global.anthropic.claude-opus-4-5-20251101-v1:0"
        self.timeout = settings.agent_timeout_seconds
        self.enable_notifications = settings.enable_notifications

        logger.info("Notification Agent initialized successfully")

    def queue_decision_notification(
        self,
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
        """Queue decision notification for delivery.

        Args:
            application_id: Unique application ID
            applicant_name: Applicant name
            applicant_email: Email address
            applicant_phone: Phone number (optional)
            classification: Decision classification
            risk_score: Risk assessment score
            approved_amount: Approved loan amount (if approved)
            recommended_rate: Recommended interest rate (if applicable)
            reasoning: Decision reasoning

        Returns:
            Dictionary with notification queue status
        """
        try:
            logger.info(
                f"Queuing decision notification for {application_id}",
                extra={
                    "classification": classification,
                    "applicant_email": applicant_email,
                },
            )

            # Determine template and channels
            template_type = self._determine_template(classification)
            notification_channels = self._determine_channels(applicant_phone)

            # Generate notification content for each channel
            notifications = []
            for channel in notification_channels:
                notification = self._generate_notification(
                    application_id=application_id,
                    template_type=template_type,
                    channel=channel,
                    applicant_name=applicant_name,
                    applicant_email=applicant_email,
                    applicant_phone=applicant_phone,
                    classification=classification,
                    risk_score=risk_score,
                    approved_amount=approved_amount,
                    recommended_rate=recommended_rate,
                    reasoning=reasoning,
                )
                notifications.append(notification)

            result = {
                "application_id": application_id,
                "notifications_queued": len(notifications),
                "template_type": template_type.value,
                "channels": [n["channel"] for n in notifications],
                "notifications": notifications,
                "queue_status": {
                    "queued_at": datetime.utcnow().isoformat(),
                    "delivery_started_at": None,
                    "delivery_completed_at": None,
                    "retry_count": 0,
                    "max_retries": 3,
                },
                "audit": {
                    "applicant_name": applicant_name,
                    "applicant_email": applicant_email,
                    "classification": classification,
                    "notification_purpose": "Decision delivery",
                },
            }

            logger.info(
                f"Queued {len(notifications)} notifications for {application_id}",
                extra={
                    "channels": [n["channel"] for n in notifications],
                    "template": template_type.value,
                },
            )

            return result

        except Exception as e:
            logger.error(
                f"Failed to queue notification: {str(e)}",
                exc_info=True,
            )
            raise AgentException(
                f"Failed to queue notification: {str(e)}", agent_name="NotificationAgent"
            )

    def queue_appeal_notification(
        self,
        application_id: str,
        applicant_name: str,
        applicant_email: str,
        appeal_status: str,
        appeal_decision: Optional[str] = None,
        original_decision: Optional[str] = None,
        new_decision: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Queue appeal-related notification.

        Args:
            application_id: Application ID
            applicant_name: Applicant name
            applicant_email: Email address
            appeal_status: Status of appeal (received/approved/rejected/pending)
            appeal_decision: New decision if appeal completed
            original_decision: Original decision classification
            new_decision: New decision classification

        Returns:
            Dictionary with appeal notification details
        """
        try:
            logger.info(
                f"Queuing appeal notification for {application_id}",
                extra={"appeal_status": appeal_status},
            )

            # Determine template based on appeal status
            if appeal_status == "received":
                template_type = NotificationTemplate.APPEAL_RECEIVED
            elif appeal_status == "approved":
                template_type = NotificationTemplate.APPEAL_APPROVED
            elif appeal_status == "rejected":
                template_type = NotificationTemplate.APPEAL_REJECTED
            else:
                template_type = NotificationTemplate.APPEAL_RECEIVED

            # Generate email notification
            email_content = self._generate_appeal_email(
                application_id=application_id,
                applicant_name=applicant_name,
                appeal_status=appeal_status,
                original_decision=original_decision,
                new_decision=new_decision,
            )

            result = {
                "application_id": application_id,
                "appeal_status": appeal_status,
                "notification_type": "appeal_notification",
                "email": {
                    "recipient": applicant_email,
                    "subject": email_content["subject"],
                    "body": email_content["body"],
                    "status": "queued",
                    "queued_at": datetime.utcnow().isoformat(),
                },
                "metadata": {
                    "original_decision": original_decision,
                    "new_decision": new_decision,
                    "template": template_type.value,
                },
            }

            logger.info(
                f"Queued appeal notification for {application_id}",
                extra={"appeal_status": appeal_status},
            )

            return result

        except Exception as e:
            logger.error(
                f"Failed to queue appeal notification: {str(e)}",
                exc_info=True,
            )
            raise AgentException(
                f"Failed to queue appeal notification: {str(e)}", agent_name="NotificationAgent"
            )

    def _determine_template(self, classification: str) -> NotificationTemplate:
        """Determine which notification template to use."""
        if classification == DecisionClassification.APPROVED:
            return NotificationTemplate.APPROVED
        elif classification == DecisionClassification.REJECTED:
            return NotificationTemplate.REJECTED
        else:
            return NotificationTemplate.UNDER_REVIEW

    def _determine_channels(self, phone_number: Optional[str]) -> List[NotificationChannel]:
        """Determine which notification channels to use."""
        channels = [NotificationChannel.EMAIL]
        if phone_number and self.enable_notifications:
            channels.append(NotificationChannel.SMS)
        channels.append(NotificationChannel.IN_APP)
        return channels

    def _generate_notification(
        self,
        application_id: str,
        template_type: NotificationTemplate,
        channel: NotificationChannel,
        applicant_name: str,
        applicant_email: str,
        applicant_phone: Optional[str],
        classification: str,
        risk_score: float,
        approved_amount: Optional[float],
        recommended_rate: Optional[float],
        reasoning: Optional[str],
    ) -> Dict[str, Any]:
        """Generate notification content for specific channel."""
        if channel == NotificationChannel.EMAIL:
            return self._generate_email_notification(
                application_id,
                template_type,
                applicant_name,
                applicant_email,
                classification,
                approved_amount,
                recommended_rate,
                reasoning,
            )
        elif channel == NotificationChannel.SMS:
            return self._generate_sms_notification(
                application_id,
                template_type,
                applicant_name,
                applicant_phone,
                classification,
            )
        else:
            return self._generate_in_app_notification(
                application_id,
                template_type,
                applicant_name,
                classification,
            )

    def _generate_email_notification(
        self,
        application_id: str,
        template_type: NotificationTemplate,
        applicant_name: str,
        applicant_email: str,
        classification: str,
        approved_amount: Optional[float],
        recommended_rate: Optional[float],
        reasoning: Optional[str],
    ) -> Dict[str, Any]:
        """Generate email notification."""
        subject, body = self._get_email_template(
            template_type,
            applicant_name,
            approved_amount,
            recommended_rate,
            reasoning,
        )

        return {
            "channel": NotificationChannel.EMAIL.value,
            "recipient": applicant_email,
            "subject": subject,
            "body": body,
            "status": "queued",
            "queued_at": datetime.utcnow().isoformat(),
            "delivery_attempts": 0,
            "max_attempts": 3,
            "retry_delay_minutes": 5,
        }

    def _generate_sms_notification(
        self,
        application_id: str,
        template_type: NotificationTemplate,
        applicant_name: str,
        applicant_phone: str,
        classification: str,
    ) -> Dict[str, Any]:
        """Generate SMS notification."""
        if classification == DecisionClassification.APPROVED:
            message = f"Good news {applicant_name}! Your loan application ({application_id[:8]}) has been APPROVED. Check your email for details."
        elif classification == DecisionClassification.REJECTED:
            message = f"Your loan application ({application_id[:8]}) has been REJECTED. You have 30 days to appeal. Check your email for details."
        else:
            message = f"Your loan application ({application_id[:8]}) is UNDER REVIEW. We will notify you soon. Check your email for updates."

        return {
            "channel": NotificationChannel.SMS.value,
            "recipient": applicant_phone,
            "message": message,
            "status": "queued",
            "queued_at": datetime.utcnow().isoformat(),
            "delivery_attempts": 0,
            "max_attempts": 3,
        }

    def _generate_in_app_notification(
        self,
        application_id: str,
        template_type: NotificationTemplate,
        applicant_name: str,
        classification: str,
    ) -> Dict[str, Any]:
        """Generate in-app notification."""
        if classification == DecisionClassification.APPROVED:
            title = "Application Approved"
            message = "Congratulations! Your loan application has been approved. Check your email for details."
        elif classification == DecisionClassification.REJECTED:
            title = "Application Rejected"
            message = "Your loan application was not approved at this time. You have 30 days to appeal. See email for details."
        else:
            title = "Application Under Review"
            message = "Your application is currently under review. We will notify you when a decision is made."

        return {
            "channel": NotificationChannel.IN_APP.value,
            "title": title,
            "message": message,
            "status": "queued",
            "queued_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "read": False,
        }

    def _get_email_template(
        self,
        template_type: NotificationTemplate,
        applicant_name: str,
        approved_amount: Optional[float],
        recommended_rate: Optional[float],
        reasoning: Optional[str],
    ) -> tuple[str, str]:
        """Get email template content."""
        if template_type == NotificationTemplate.APPROVED:
            subject = "Loan Application Approved"
            amount_str = f"${approved_amount:,.2f}" if approved_amount else "To be determined"
            rate_str = f"{recommended_rate:.2f}%" if recommended_rate else "To be determined"
            body = f"""
Dear {applicant_name},

We are delighted to inform you that your loan application has been APPROVED!

APPROVAL DETAILS:
- Approved Amount: {amount_str}
- Recommended Interest Rate: {rate_str}
- Your application has been processed successfully and meets our lending criteria.

NEXT STEPS:
1. Review your approval letter and loan terms (attached)
2. Schedule a call with our loan officer to finalize documentation
3. Expected funding: Within 5-7 business days

If you have any questions about your approval, please contact us at:
Phone: 1-800-LOAN-APP
Email: support@loanapp.com

Thank you for choosing us!

Best regards,
Loan Approval System
            """.strip()

        elif template_type == NotificationTemplate.REJECTED:
            subject = "Loan Application Decision - Appeal Available"
            body = f"""
Dear {applicant_name},

Thank you for your loan application. After careful review, we are unable to approve your application at this time.

DECISION REASON:
{reasoning or 'Your creditworthiness profile did not meet our lending criteria.'}

YOUR RIGHTS:
You have the right to appeal this decision within 30 days. Please see the attached adverse action notice for complete information about your appeal rights and next steps.

TO APPEAL:
- Reply to this email with "APPEAL REQUEST"
- Call 1-800-LOAN-APP to speak with a loan officer
- Visit www.loanapp.com/appeal to submit your appeal online

We encourage you to review your credit report and reach out if you have questions.

Best regards,
Loan Approval System
            """.strip()

        else:  # UNDER_REVIEW
            subject = "Loan Application Status Update"
            body = f"""
Dear {applicant_name},

Your loan application is currently under review by our lending team.

STATUS: Under Review
We are carefully evaluating your application and will have a decision for you shortly.

WHAT TO EXPECT:
- Review timeline: 3-5 business days
- You will receive a notification when a decision is made
- You can check your status anytime by logging into your account

If you have questions about your application, contact us at:
Phone: 1-800-LOAN-APP
Email: support@loanapp.com

Thank you for your patience!

Best regards,
Loan Approval System
            """.strip()

        return subject, body

    def _generate_appeal_email(
        self,
        application_id: str,
        applicant_name: str,
        appeal_status: str,
        original_decision: Optional[str],
        new_decision: Optional[str],
    ) -> Dict[str, str]:
        """Generate appeal-related email content."""
        if appeal_status == "received":
            subject = "Appeal Received - Reference Number"
            body = f"""
Dear {applicant_name},

We have received your appeal for application {application_id}.

APPEAL STATUS: Received and Under Review
Reference Number: {application_id}
Review Timeline: 10-15 business days
Next Update: Within 7 business days

Your appeal has been assigned to a senior loan officer for comprehensive review. We will consider any additional information you have provided.

You will be notified via email once a decision has been made on your appeal.

Thank you for appealing,
Loan Approval System
            """.strip()

        elif appeal_status == "approved":
            subject = "Appeal Approved - Your Loan Has Been Approved"
            body = f"""
Dear {applicant_name},

Great news! Your appeal has been approved.

ORIGINAL DECISION: {original_decision}
NEW DECISION: {new_decision}

Your loan application is now APPROVED. A loan officer will contact you within 1 business day to finalize the terms and next steps.

Congratulations!
Loan Approval System
            """.strip()

        else:  # rejected
            subject = "Appeal Review Complete"
            body = f"""
Dear {applicant_name},

We have completed our review of your appeal for application {application_id}.

APPEAL STATUS: Reviewed
DECISION: Your appeal was not approved at this time

The senior loan officer reviewed your application and additional information you provided. Based on this comprehensive review, our lending criteria were not fully satisfied.

You have the right to request an explanation of this decision. Please contact us for more information.

Thank you,
Loan Approval System
            """.strip()

        return {"subject": subject, "body": body}
