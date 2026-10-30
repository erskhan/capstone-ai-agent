"""Service for managing loan appeals and manual reviews."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import uuid4
from sqlalchemy.orm import Session

from shared.logger import get_logger
from shared.exceptions import AgentException

logger = get_logger("appeal_service")


class AppealService:
    """Manages loan application appeals and manual review queue."""

    @staticmethod
    def create_appeal(
        db: Session,
        application_id: str,
        appeal_reason: str,
        additional_documentation: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new appeal for a rejected application.

        Args:
            db: Database session
            application_id: Application ID
            appeal_reason: Reason for appeal
            additional_documentation: Additional supporting documentation
            contact_email: Contact email for appeal
            contact_phone: Contact phone for appeal

        Returns:
            Dictionary with appeal creation result
        """
        try:
            from database.models import AppealModel

            appeal_id = str(uuid4())
            appeal = AppealModel(
                id=appeal_id,
                application_id=application_id,
                appeal_reason=appeal_reason,
                additional_documentation=additional_documentation,
                contact_email=contact_email,
                contact_phone=contact_phone,
                status="received",
                submitted_at=datetime.utcnow(),
            )

            db.add(appeal)
            db.commit()
            db.refresh(appeal)

            logger.info(
                f"Created appeal {appeal_id} for application {application_id}",
                extra={"appeal_id": appeal_id},
            )

            return {
                "appeal_id": appeal_id,
                "application_id": application_id,
                "status": "received",
                "submitted_at": appeal.submitted_at.isoformat(),
                "expected_decision_date": (
                    datetime.utcnow() + timedelta(days=15)
                ).isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Error creating appeal: {str(e)}",
                extra={"application_id": application_id},
            )
            db.rollback()
            raise AgentException(
                f"Failed to create appeal: {str(e)}", agent_name="AppealService"
            )

    @staticmethod
    def get_appeal(db: Session, appeal_id: str) -> Optional[Dict[str, Any]]:
        """Get appeal details by ID.

        Args:
            db: Database session
            appeal_id: Appeal ID

        Returns:
            Dictionary with appeal details or None
        """
        try:
            from database.models import AppealModel

            appeal = db.query(AppealModel).filter_by(id=appeal_id).first()

            if not appeal:
                logger.debug(f"Appeal {appeal_id} not found")
                return None

            return {
                "appeal_id": appeal.id,
                "application_id": appeal.application_id,
                "status": appeal.status,
                "appeal_reason": appeal.appeal_reason,
                "submitted_at": appeal.submitted_at.isoformat() if appeal.submitted_at else None,
                "decision_at": appeal.decision_at.isoformat() if appeal.decision_at else None,
                "decision": appeal.decision,
                "reviewer_notes": appeal.reviewer_notes,
            }

        except Exception as e:
            logger.error(f"Error retrieving appeal: {str(e)}")
            raise

    @staticmethod
    def assign_to_manual_review(
        db: Session,
        application_id: str,
        reason: str,
        assigned_to: Optional[str] = None,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """Assign application to manual review queue.

        Args:
            db: Database session
            application_id: Application ID
            reason: Reason for manual review
            assigned_to: Reviewer name or ID
            priority: Review priority level

        Returns:
            Dictionary with review assignment details
        """
        try:
            from database.models import ManualReviewModel

            review_id = str(uuid4())
            manual_review = ManualReviewModel(
                id=review_id,
                application_id=application_id,
                reason=reason,
                assigned_to=assigned_to,
                priority=priority,
                status="assigned",
                assigned_at=datetime.utcnow(),
            )

            db.add(manual_review)
            db.commit()
            db.refresh(manual_review)

            logger.info(
                f"Assigned application {application_id} to manual review",
                extra={
                    "review_id": review_id,
                    "priority": priority,
                },
            )

            return {
                "review_id": review_id,
                "application_id": application_id,
                "status": "assigned",
                "priority": priority,
                "assigned_at": manual_review.assigned_at.isoformat(),
                "estimated_completion": (
                    datetime.utcnow() + timedelta(days=3)
                ).isoformat(),
                "assigned_to": assigned_to,
            }

        except Exception as e:
            logger.error(
                f"Error assigning to manual review: {str(e)}",
                extra={"application_id": application_id},
            )
            db.rollback()
            raise AgentException(
                f"Failed to assign to manual review: {str(e)}", agent_name="AppealService"
            )

    @staticmethod
    def get_manual_review_queue(
        db: Session, priority: Optional[str] = None, status: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """Get manual review queue.

        Args:
            db: Database session
            priority: Filter by priority level
            status: Filter by status

        Returns:
            List of review items in queue
        """
        try:
            from database.models import ManualReviewModel

            query = db.query(ManualReviewModel)

            if priority:
                query = query.filter_by(priority=priority)
            if status:
                query = query.filter_by(status=status)

            reviews = query.order_by(
                ManualReviewModel.priority.desc(), ManualReviewModel.assigned_at.asc()
            ).all()

            return [
                {
                    "review_id": r.id,
                    "application_id": r.application_id,
                    "status": r.status,
                    "priority": r.priority,
                    "reason": r.reason,
                    "assigned_to": r.assigned_to,
                    "assigned_at": r.assigned_at.isoformat() if r.assigned_at else None,
                    "completed_at": r.completed_at.isoformat()
                    if r.completed_at
                    else None,
                }
                for r in reviews
            ]

        except Exception as e:
            logger.error(f"Error retrieving manual review queue: {str(e)}")
            raise

    @staticmethod
    def complete_manual_review(
        db: Session,
        review_id: str,
        decision: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mark manual review as complete.

        Args:
            db: Database session
            review_id: Manual review ID
            decision: Review decision (approved/rejected/maintain)
            notes: Reviewer notes

        Returns:
            Dictionary with completion details
        """
        try:
            from database.models import ManualReviewModel

            review = db.query(ManualReviewModel).filter_by(id=review_id).first()

            if not review:
                raise ValueError(f"Manual review {review_id} not found")

            review.status = "completed"
            review.decision = decision
            review.reviewer_notes = notes
            review.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(review)

            logger.info(
                f"Completed manual review {review_id}",
                extra={
                    "application_id": review.application_id,
                    "decision": decision,
                },
            )

            return {
                "review_id": review_id,
                "application_id": review.application_id,
                "status": "completed",
                "decision": decision,
                "completed_at": review.completed_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error completing manual review: {str(e)}")
            db.rollback()
            raise AgentException(
                f"Failed to complete manual review: {str(e)}", agent_name="AppealService"
            )
