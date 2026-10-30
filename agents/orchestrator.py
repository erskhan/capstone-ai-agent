"""LangGraph orchestration workflow for loan approval."""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum

from models.schemas import LoanApplicationRequest, ApplicationStatus
from agents.applicant_agent import ApplicantProfileAgent
from agents.risk_agent import FinancialRiskAnalysisAgent
from agents.decision_agent import LoanDecisionAgent
from agents.compliance_agent import ComplianceAgent
from agents.notification_agent import NotificationAgent
from shared.logger import get_logger
from shared.exceptions import AgentException, WorkflowException

logger = get_logger("orchestrator")


class WorkflowState(str, Enum):
    """Workflow execution state."""

    STARTED = "started"
    VALIDATING = "validating"
    ANALYZING_APPLICANT = "analyzing_applicant"
    ANALYZING_RISK = "analyzing_risk"
    SYNTHESIZING_DECISION = "synthesizing_decision"
    VALIDATING_COMPLIANCE = "validating_compliance"
    QUEUEING_NOTIFICATIONS = "queueing_notifications"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStep:
    """Represents a step in the workflow."""

    def __init__(self, name: str, status: str = "pending", result: Optional[Dict] = None, error: Optional[str] = None):
        """Initialize workflow step."""
        self.name = name
        self.status = status
        self.result = result or {}
        self.error = error
        self.started_at = None
        self.completed_at = None

    def to_dict(self) -> dict:
        """Convert step to dictionary."""
        return {
            "name": self.name,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class LoanApprovalOrchestrator:
    """Orchestrates multi-agent loan approval workflow using LangGraph patterns."""

    def __init__(self):
        """Initialize orchestrator with all required agents."""
        self.applicant_agent = ApplicantProfileAgent()
        self.risk_agent = FinancialRiskAnalysisAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceAgent()
        self.notification_agent = NotificationAgent()

        logger.info("Loan approval orchestrator initialized with all agents")

    def process_application(
        self, application: LoanApplicationRequest, application_id: str, correlation_id: str
    ) -> Dict[str, Any]:
        """Process a loan application through the complete workflow.

        Workflow steps:
        1. Validate input
        2. Analyze applicant profile
        3. Analyze financial risk
        4. Synthesize decision
        5. Return results

        Args:
            application: Loan application request
            application_id: Unique application ID
            correlation_id: Correlation ID for tracking

        Returns:
            Dictionary with workflow results and decision
        """
        workflow_state = WorkflowState.STARTED
        steps = []

        try:
            logger.info(
                f"Starting application processing: {application_id}",
                extra={"correlation_id": correlation_id},
            )

            # Step 1: Validate input
            validate_step = WorkflowStep("validate_input")
            validate_step.started_at = datetime.utcnow()
            try:
                self._validate_application(application)
                validate_step.status = "completed"
                validate_step.result = {"validation": "passed"}
                workflow_state = WorkflowState.VALIDATING
            except Exception as e:
                validate_step.status = "failed"
                validate_step.error = str(e)
                raise
            finally:
                validate_step.completed_at = datetime.utcnow()
                steps.append(validate_step)

            # Step 2: Analyze applicant profile
            applicant_step = WorkflowStep("analyze_applicant_profile")
            applicant_step.started_at = datetime.utcnow()
            try:
                workflow_state = WorkflowState.ANALYZING_APPLICANT
                logger.info(
                    "Starting applicant profile analysis",
                    extra={"correlation_id": correlation_id},
                )

                applicant_result = self.applicant_agent.analyze(
                    applicant=application.applicant_profile,
                    employment=application.employment_info,
                    credit=application.credit_record,
                )

                applicant_step.status = "completed"
                applicant_step.result = applicant_result
                logger.info(
                    f"Applicant profile analysis completed with status: {applicant_result.get('validation_status')}",
                    extra={"correlation_id": correlation_id},
                )
            except Exception as e:
                applicant_step.status = "failed"
                applicant_step.error = str(e)
                logger.error(
                    f"Applicant profile analysis failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
                raise
            finally:
                applicant_step.completed_at = datetime.utcnow()
                steps.append(applicant_step)

            # Step 3: Analyze financial risk
            risk_step = WorkflowStep("analyze_financial_risk")
            risk_step.started_at = datetime.utcnow()
            try:
                workflow_state = WorkflowState.ANALYZING_RISK
                logger.info(
                    "Starting financial risk analysis",
                    extra={"correlation_id": correlation_id},
                )

                risk_result = self.risk_agent.analyze(application)

                risk_step.status = "completed"
                risk_step.result = risk_result
                logger.info(
                    f"Financial risk analysis completed with risk score: {risk_result.get('risk_score'):.0f}",
                    extra={"correlation_id": correlation_id},
                )
            except Exception as e:
                risk_step.status = "failed"
                risk_step.error = str(e)
                logger.error(
                    f"Financial risk analysis failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
                raise
            finally:
                risk_step.completed_at = datetime.utcnow()
                steps.append(risk_step)

            # Step 4: Synthesize decision
            decision_step = WorkflowStep("synthesize_decision")
            decision_step.started_at = datetime.utcnow()
            try:
                workflow_state = WorkflowState.SYNTHESIZING_DECISION
                logger.info(
                    "Starting decision synthesis",
                    extra={"correlation_id": correlation_id},
                )

                decision_result = self.decision_agent.decide(
                    application=application,
                    applicant_analysis=applicant_result,
                    risk_analysis=risk_result,
                )

                decision_step.status = "completed"
                decision_step.result = decision_result
                logger.info(
                    f"Decision synthesis completed: {decision_result.get('classification_value')}",
                    extra={"correlation_id": correlation_id},
                )
            except Exception as e:
                decision_step.status = "failed"
                decision_step.error = str(e)
                logger.error(
                    f"Decision synthesis failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
                raise
            finally:
                decision_step.completed_at = datetime.utcnow()
                steps.append(decision_step)

            # Step 4: Validate compliance
            compliance_step = WorkflowStep("validate_compliance")
            compliance_step.started_at = datetime.utcnow()
            compliance_result = None
            try:
                workflow_state = WorkflowState.VALIDATING_COMPLIANCE
                logger.info(
                    "Starting compliance validation",
                    extra={"correlation_id": correlation_id},
                )

                compliance_result = self.compliance_agent.validate_and_process(
                    application_id,
                    decision_result.get("classification_value"),
                    risk_result.get("risk_score", 0),
                    f"{application.applicant_profile.first_name} {application.applicant_profile.last_name}",
                    application.applicant_profile.email,
                    application.loan_details.loan_amount,
                    decision_result.get("reasoning", ""),
                )

                compliance_step.status = "completed"
                compliance_step.result = compliance_result
                logger.info(
                    "Compliance validation completed",
                    extra={
                        "correlation_id": correlation_id,
                        "validation_passed": compliance_result.get("compliance_validation_passed"),
                    },
                )
            except Exception as e:
                compliance_step.status = "failed"
                compliance_step.error = str(e)
                logger.warning(
                    f"Compliance validation failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
            finally:
                compliance_step.completed_at = datetime.utcnow()
                steps.append(compliance_step)

            # Step 5: Queue notifications
            notification_step = WorkflowStep("queue_notifications")
            notification_step.started_at = datetime.utcnow()
            notification_result = None
            try:
                workflow_state = WorkflowState.QUEUEING_NOTIFICATIONS
                logger.info(
                    "Starting notification queuing",
                    extra={"correlation_id": correlation_id},
                )

                notification_result = self.notification_agent.queue_decision_notification(
                    application_id,
                    f"{application.applicant_profile.first_name} {application.applicant_profile.last_name}",
                    application.applicant_profile.email,
                    application.applicant_profile.phone,
                    decision_result.get("classification_value"),
                    risk_result.get("risk_score", 0),
                    decision_result.get("approved_loan_amount"),
                    decision_result.get("recommended_rate"),
                    decision_result.get("reasoning"),
                )

                notification_step.status = "completed"
                notification_step.result = notification_result
                logger.info(
                    f"Notifications queued: {notification_result.get('notifications_queued')} notifications",
                    extra={"correlation_id": correlation_id},
                )
            except Exception as e:
                notification_step.status = "failed"
                notification_step.error = str(e)
                logger.warning(
                    f"Notification queuing failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
            finally:
                notification_step.completed_at = datetime.utcnow()
                steps.append(notification_step)

            workflow_state = WorkflowState.COMPLETED

            # Compile final result
            result = {
                "application_id": application_id,
                "correlation_id": correlation_id,
                "workflow_state": workflow_state.value,
                "status": ApplicationStatus.APPROVED if decision_result["classification_value"] == "approved" else ApplicationStatus.UNDER_REVIEW,
                "completed_at": datetime.utcnow().isoformat(),
                "steps": [step.to_dict() for step in steps],
                "applicant_analysis": applicant_result,
                "risk_analysis": risk_result,
                "decision": decision_result,
                "compliance": compliance_result,
                "notifications": notification_result,
            }

            logger.info(
                f"Application processing completed successfully: {application_id}",
                extra={"correlation_id": correlation_id, "decision": decision_result.get("classification_value")},
            )

            return result

        except Exception as e:
            workflow_state = WorkflowState.FAILED
            logger.error(
                f"Application processing failed: {str(e)}",
                extra={"correlation_id": correlation_id},
                exc_info=True,
            )

            return {
                "application_id": application_id,
                "correlation_id": correlation_id,
                "workflow_state": workflow_state.value,
                "status": ApplicationStatus.REJECTED,
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat(),
                "steps": [step.to_dict() for step in steps],
            }

    async def process_application_async(
        self, application: LoanApplicationRequest, application_id: str, correlation_id: str
    ) -> Dict[str, Any]:
        """Process application with parallel agent execution.

        Workflow steps:
        1. Validate input
        2. Analyze applicant profile AND financial risk IN PARALLEL
        3. Synthesize decision (after both analyses complete)
        4. Return results

        This async version reduces processing time by running applicant and risk analyses concurrently.

        Args:
            application: Loan application request
            application_id: Unique application ID
            correlation_id: Correlation ID for tracking

        Returns:
            Dictionary with workflow results and decision
        """
        workflow_state = WorkflowState.STARTED
        steps = []
        applicant_result = None
        risk_result = None

        try:
            logger.info(
                f"Starting async application processing: {application_id}",
                extra={"correlation_id": correlation_id},
            )

            # Step 1: Validate input
            validate_step = WorkflowStep("validate_input")
            validate_step.started_at = datetime.utcnow()
            try:
                self._validate_application(application)
                validate_step.status = "completed"
                validate_step.result = {"validation": "passed"}
            except Exception as e:
                validate_step.status = "failed"
                validate_step.error = str(e)
                raise
            finally:
                validate_step.completed_at = datetime.utcnow()
                steps.append(validate_step)

            # Step 2: Run applicant and risk analyses in parallel
            parallel_start = datetime.utcnow()
            try:
                logger.info(
                    "Starting parallel applicant and risk analysis",
                    extra={"correlation_id": correlation_id},
                )

                # Run both analyses concurrently
                applicant_result, risk_result = await asyncio.gather(
                    asyncio.to_thread(
                        self.applicant_agent.analyze,
                        application.applicant_profile,
                        application.employment_info,
                        application.credit_record,
                    ),
                    asyncio.to_thread(
                        self.risk_agent.analyze,
                        application,
                    ),
                    return_exceptions=False,
                )

                parallel_duration = (datetime.utcnow() - parallel_start).total_seconds()
                logger.info(
                    f"Parallel analysis completed in {parallel_duration:.2f}s",
                    extra={
                        "correlation_id": correlation_id,
                        "applicant_status": applicant_result.get("validation_status"),
                        "risk_score": risk_result.get("risk_score"),
                    },
                )

                # Record both steps
                applicant_step = WorkflowStep("analyze_applicant_profile")
                applicant_step.started_at = parallel_start
                applicant_step.completed_at = datetime.utcnow()
                applicant_step.status = "completed"
                applicant_step.result = applicant_result
                steps.append(applicant_step)

                risk_step = WorkflowStep("analyze_financial_risk")
                risk_step.started_at = parallel_start
                risk_step.completed_at = datetime.utcnow()
                risk_step.status = "completed"
                risk_step.result = risk_result
                steps.append(risk_step)

            except Exception as e:
                logger.error(
                    f"Parallel analysis failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
                raise

            # Step 3: Synthesize decision (uses results from parallel analyses)
            decision_step = WorkflowStep("synthesize_decision")
            decision_step.started_at = datetime.utcnow()
            try:
                workflow_state = WorkflowState.SYNTHESIZING_DECISION
                logger.info(
                    "Starting decision synthesis",
                    extra={"correlation_id": correlation_id},
                )

                decision_result = await asyncio.to_thread(
                    self.decision_agent.decide,
                    application,
                    applicant_result,
                    risk_result,
                )

                decision_step.status = "completed"
                decision_step.result = decision_result
                logger.info(
                    f"Decision synthesis completed: {decision_result.get('classification_value')}",
                    extra={"correlation_id": correlation_id},
                )
            except Exception as e:
                decision_step.status = "failed"
                decision_step.error = str(e)
                logger.error(
                    f"Decision synthesis failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
                raise
            finally:
                decision_step.completed_at = datetime.utcnow()
                steps.append(decision_step)

            # Step 4: Validate compliance
            compliance_step = WorkflowStep("validate_compliance")
            compliance_step.started_at = datetime.utcnow()
            compliance_result = None
            try:
                workflow_state = WorkflowState.VALIDATING_COMPLIANCE
                logger.info(
                    "Starting compliance validation",
                    extra={"correlation_id": correlation_id},
                )

                compliance_result = await asyncio.to_thread(
                    self.compliance_agent.validate_and_process,
                    application_id,
                    decision_result.get("classification_value"),
                    risk_result.get("risk_score", 0),
                    f"{application.applicant_profile.first_name} {application.applicant_profile.last_name}",
                    application.applicant_profile.email,
                    application.loan_details.loan_amount,
                    decision_result.get("reasoning", ""),
                )

                compliance_step.status = "completed"
                compliance_step.result = compliance_result
                logger.info(
                    "Compliance validation completed",
                    extra={
                        "correlation_id": correlation_id,
                        "validation_passed": compliance_result.get("compliance_validation_passed"),
                    },
                )
            except Exception as e:
                compliance_step.status = "failed"
                compliance_step.error = str(e)
                logger.warning(
                    f"Compliance validation failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
            finally:
                compliance_step.completed_at = datetime.utcnow()
                steps.append(compliance_step)

            # Step 5: Queue notifications
            notification_step = WorkflowStep("queue_notifications")
            notification_step.started_at = datetime.utcnow()
            notification_result = None
            try:
                workflow_state = WorkflowState.QUEUEING_NOTIFICATIONS
                logger.info(
                    "Starting notification queuing",
                    extra={"correlation_id": correlation_id},
                )

                notification_result = await asyncio.to_thread(
                    self.notification_agent.queue_decision_notification,
                    application_id,
                    f"{application.applicant_profile.first_name} {application.applicant_profile.last_name}",
                    application.applicant_profile.email,
                    application.applicant_profile.phone,
                    decision_result.get("classification_value"),
                    risk_result.get("risk_score", 0),
                    decision_result.get("approved_loan_amount"),
                    decision_result.get("recommended_rate"),
                    decision_result.get("reasoning"),
                )

                notification_step.status = "completed"
                notification_step.result = notification_result
                logger.info(
                    f"Notifications queued: {notification_result.get('notifications_queued')} notifications",
                    extra={"correlation_id": correlation_id},
                )
            except Exception as e:
                notification_step.status = "failed"
                notification_step.error = str(e)
                logger.warning(
                    f"Notification queuing failed: {str(e)}",
                    extra={"correlation_id": correlation_id},
                )
            finally:
                notification_step.completed_at = datetime.utcnow()
                steps.append(notification_step)

            workflow_state = WorkflowState.COMPLETED

            # Compile final result
            result = {
                "application_id": application_id,
                "correlation_id": correlation_id,
                "workflow_state": workflow_state.value,
                "parallel_execution": True,
                "status": ApplicationStatus.APPROVED if decision_result["classification_value"] == "approved" else ApplicationStatus.UNDER_REVIEW,
                "completed_at": datetime.utcnow().isoformat(),
                "steps": [step.to_dict() for step in steps],
                "applicant_analysis": applicant_result,
                "risk_analysis": risk_result,
                "decision": decision_result,
                "compliance": compliance_result,
                "notifications": notification_result,
            }

            logger.info(
                f"Async application processing completed successfully: {application_id}",
                extra={"correlation_id": correlation_id, "decision": decision_result.get("classification_value")},
            )

            return result

        except Exception as e:
            workflow_state = WorkflowState.FAILED
            logger.error(
                f"Async application processing failed: {str(e)}",
                extra={"correlation_id": correlation_id},
                exc_info=True,
            )

            return {
                "application_id": application_id,
                "correlation_id": correlation_id,
                "workflow_state": workflow_state.value,
                "parallel_execution": True,
                "status": ApplicationStatus.REJECTED,
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat(),
                "steps": [step.to_dict() for step in steps],
            }

    def _validate_application(self, application: LoanApplicationRequest) -> None:
        """Validate loan application data."""
        if not application:
            raise WorkflowException("Application is required")

        # Basic validation
        if application.loan_details.loan_amount <= 0:
            raise WorkflowException("Loan amount must be positive")

        if application.employment_info.annual_income <= 0:
            raise WorkflowException("Annual income must be positive")

        if application.credit_record.credit_score < 300 or application.credit_record.credit_score > 850:
            raise WorkflowException(
                f"Credit score {application.credit_record.credit_score} out of valid range (300-850)"
            )

        logger.debug("Application validation passed")
