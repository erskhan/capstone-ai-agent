"""Database service for workflow state persistence and retrieval."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from database.models import WorkflowExecutionModel, AuditLogModel
from shared.logger import get_logger

logger = get_logger("db_service")


class WorkflowStateService:
    """Service for persisting and retrieving workflow execution state."""

    @staticmethod
    def create_workflow_execution(
        db: Session,
        application_id: str,
        correlation_id: str,
    ) -> WorkflowExecutionModel:
        """Create a new workflow execution record.

        Args:
            db: Database session
            application_id: Application ID
            correlation_id: Correlation ID for tracking

        Returns:
            Created WorkflowExecutionModel
        """
        try:
            execution = WorkflowExecutionModel(
                id=str(uuid4()),
                application_id=application_id,
                correlation_id=correlation_id,
                workflow_state="started",
                current_step="validate",
                attempt_number=1,
            )
            db.add(execution)
            db.commit()
            db.refresh(execution)

            logger.info(
                f"Created workflow execution for application {application_id}",
                extra={
                    "execution_id": execution.id,
                    "correlation_id": correlation_id,
                },
            )
            return execution

        except Exception as e:
            logger.error(
                f"Error creating workflow execution: {str(e)}",
                extra={"application_id": application_id},
            )
            db.rollback()
            raise

    @staticmethod
    def get_workflow_execution(
        db: Session,
        application_id: str,
    ) -> Optional[WorkflowExecutionModel]:
        """Get workflow execution for an application.

        Args:
            db: Database session
            application_id: Application ID

        Returns:
            WorkflowExecutionModel or None if not found
        """
        try:
            execution = db.query(WorkflowExecutionModel).filter_by(
                application_id=application_id
            ).first()

            if execution:
                logger.debug(
                    f"Retrieved workflow execution for application {application_id}",
                    extra={"state": execution.workflow_state, "step": execution.current_step},
                )
            else:
                logger.debug(f"No workflow execution found for application {application_id}")

            return execution

        except Exception as e:
            logger.error(
                f"Error retrieving workflow execution: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def update_step(
        db: Session,
        execution_id: str,
        step: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecutionModel:
        """Update workflow to next step.

        Args:
            db: Database session
            execution_id: Workflow execution ID
            step: Next step name (applicant, risk, decision, etc)
            result: Step result (optional)

        Returns:
            Updated WorkflowExecutionModel
        """
        try:
            execution = db.query(WorkflowExecutionModel).filter_by(id=execution_id).first()
            if not execution:
                raise ValueError(f"Workflow execution {execution_id} not found")

            execution.workflow_state = "in_progress"
            execution.current_step = step
            execution.step_started_at = datetime.utcnow()

            # Store result in appropriate field based on step
            if step == "applicant":
                execution.applicant_result = result
            elif step == "risk":
                execution.risk_result = result
            elif step == "decision":
                execution.decision_result = result

            db.commit()
            db.refresh(execution)

            logger.debug(
                f"Updated workflow execution to step: {step}",
                extra={"execution_id": execution_id},
            )
            return execution

        except Exception as e:
            logger.error(
                f"Error updating workflow step: {str(e)}",
                extra={"execution_id": execution_id, "step": step},
            )
            db.rollback()
            raise

    @staticmethod
    def mark_completed(
        db: Session,
        execution_id: str,
        final_decision: Dict[str, Any],
    ) -> WorkflowExecutionModel:
        """Mark workflow as completed.

        Args:
            db: Database session
            execution_id: Workflow execution ID
            final_decision: Final decision result

        Returns:
            Updated WorkflowExecutionModel
        """
        try:
            execution = db.query(WorkflowExecutionModel).filter_by(id=execution_id).first()
            if not execution:
                raise ValueError(f"Workflow execution {execution_id} not found")

            execution.workflow_state = "completed"
            execution.current_step = "complete"
            execution.decision_result = final_decision
            execution.completed_at = datetime.utcnow()
            execution.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(execution)

            logger.info(
                f"Marked workflow execution as completed",
                extra={
                    "execution_id": execution_id,
                    "decision": final_decision.get("classification_value"),
                },
            )
            return execution

        except Exception as e:
            logger.error(
                f"Error marking workflow completed: {str(e)}",
                extra={"execution_id": execution_id},
            )
            db.rollback()
            raise

    @staticmethod
    def mark_failed(
        db: Session,
        execution_id: str,
        error_message: str,
        error_step: str,
        retry: bool = False,
    ) -> WorkflowExecutionModel:
        """Mark workflow as failed.

        Args:
            db: Database session
            execution_id: Workflow execution ID
            error_message: Error message
            error_step: Step that failed
            retry: Whether to prepare for retry

        Returns:
            Updated WorkflowExecutionModel
        """
        try:
            execution = db.query(WorkflowExecutionModel).filter_by(id=execution_id).first()
            if not execution:
                raise ValueError(f"Workflow execution {execution_id} not found")

            if retry and execution.attempt_number < 3:
                execution.workflow_state = "in_progress"  # Will retry
                execution.attempt_number += 1
                logger.info(
                    f"Preparing workflow for retry (attempt {execution.attempt_number})",
                    extra={"execution_id": execution_id, "step": error_step},
                )
            else:
                execution.workflow_state = "failed"
                execution.completed_at = datetime.utcnow()
                logger.error(
                    f"Marked workflow as failed",
                    extra={
                        "execution_id": execution_id,
                        "step": error_step,
                        "attempt": execution.attempt_number,
                    },
                )

            execution.error_message = error_message
            execution.error_step = error_step
            execution.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(execution)
            return execution

        except Exception as e:
            logger.error(
                f"Error marking workflow failed: {str(e)}",
                extra={"execution_id": execution_id},
            )
            db.rollback()
            raise

    @staticmethod
    def log_audit(
        db: Session,
        application_id: str,
        correlation_id: str,
        action: str,
        agent_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLogModel:
        """Create audit log entry for workflow action.

        Args:
            db: Database session
            application_id: Application ID
            correlation_id: Correlation ID
            action: Action description
            agent_name: Name of agent that performed action
            details: Additional details (JSON)

        Returns:
            Created AuditLogModel
        """
        try:
            audit_log = AuditLogModel(
                id=str(uuid4()),
                application_id=application_id,
                correlation_id=correlation_id,
                action=action,
                agent_name=agent_name,
                details=details or {},
            )
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)

            logger.debug(
                f"Created audit log: {action}",
                extra={"application_id": application_id, "agent": agent_name},
            )
            return audit_log

        except Exception as e:
            logger.error(
                f"Error creating audit log: {str(e)}",
                extra={"application_id": application_id, "action": action},
            )
            db.rollback()
            raise

    @staticmethod
    def get_workflow_state_summary(
        db: Session,
        application_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get summary of workflow execution state.

        Args:
            db: Database session
            application_id: Application ID

        Returns:
            Dictionary with workflow state summary or None
        """
        try:
            execution = db.query(WorkflowExecutionModel).filter_by(
                application_id=application_id
            ).first()

            if not execution:
                return None

            return {
                "execution_id": execution.id,
                "application_id": execution.application_id,
                "workflow_state": execution.workflow_state,
                "current_step": execution.current_step,
                "attempt_number": execution.attempt_number,
                "error_message": execution.error_message,
                "error_step": execution.error_step,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "updated_at": execution.updated_at.isoformat() if execution.updated_at else None,
                "has_applicant_result": execution.applicant_result is not None,
                "has_risk_result": execution.risk_result is not None,
                "has_decision_result": execution.decision_result is not None,
            }

        except Exception as e:
            logger.error(
                f"Error getting workflow state summary: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def get_workflow_execution_details(
        db: Session,
        application_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get full workflow execution details with all results.

        Args:
            db: Database session
            application_id: Application ID

        Returns:
            Dictionary with full execution details or None
        """
        try:
            execution = db.query(WorkflowExecutionModel).filter_by(
                application_id=application_id
            ).first()

            if not execution:
                return None

            return {
                "execution_id": execution.id,
                "application_id": execution.application_id,
                "correlation_id": execution.correlation_id,
                "workflow_state": execution.workflow_state,
                "current_step": execution.current_step,
                "attempt_number": execution.attempt_number,
                "applicant_analysis": execution.applicant_result,
                "risk_analysis": execution.risk_result,
                "decision": execution.decision_result,
                "error_message": execution.error_message,
                "error_step": execution.error_step,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "step_started_at": execution.step_started_at.isoformat() if execution.step_started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "updated_at": execution.updated_at.isoformat() if execution.updated_at else None,
            }

        except Exception as e:
            logger.error(
                f"Error getting workflow execution details: {str(e)}",
                extra={"application_id": application_id},
            )
            raise
