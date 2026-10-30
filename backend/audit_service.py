"""Service for audit trail retrieval and reporting."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from shared.logger import get_logger

logger = get_logger("audit_service")


class AuditService:
    """Manages audit trail queries and reporting."""

    @staticmethod
    def get_audit_trail(
        db: Session,
        application_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get audit trail for an application.

        Args:
            db: Database session
            application_id: Application ID
            limit: Maximum entries to return
            offset: Number of entries to skip

        Returns:
            Dictionary with audit trail data
        """
        try:
            from database.models import AuditLogModel

            query = db.query(AuditLogModel).filter_by(application_id=application_id)
            total = query.count()

            audit_logs = (
                query.order_by(AuditLogModel.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            entries = [
                {
                    "timestamp": log.created_at.isoformat() if log.created_at else None,
                    "action": log.action,
                    "agent_name": log.agent_name,
                    "details": log.details or {},
                }
                for log in audit_logs
            ]

            earliest = None
            latest = None

            if audit_logs:
                latest = audit_logs[0].created_at
                earliest = audit_logs[-1].created_at

            return {
                "application_id": application_id,
                "total_entries": total,
                "entries": entries,
                "earliest_entry": earliest.isoformat() if earliest else None,
                "latest_entry": latest.isoformat() if latest else None,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total,
            }

        except Exception as e:
            logger.error(
                f"Error retrieving audit trail: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def get_action_count_by_agent(
        db: Session,
        application_id: str,
    ) -> Dict[str, int]:
        """Get count of actions by agent for an application.

        Args:
            db: Database session
            application_id: Application ID

        Returns:
            Dictionary with agent names and action counts
        """
        try:
            from database.models import AuditLogModel
            from sqlalchemy import func

            results = (
                db.query(AuditLogModel.agent_name, func.count(AuditLogModel.id))
                .filter_by(application_id=application_id)
                .group_by(AuditLogModel.agent_name)
                .all()
            )

            return {agent: count for agent, count in results}

        except Exception as e:
            logger.error(
                f"Error counting actions by agent: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def get_workflow_timeline(
        db: Session,
        application_id: str,
    ) -> Dict[str, Any]:
        """Get workflow timeline showing key events.

        Args:
            db: Database session
            application_id: Application ID

        Returns:
            Dictionary with timeline events
        """
        try:
            from database.models import AuditLogModel

            audit_logs = (
                db.query(AuditLogModel)
                .filter_by(application_id=application_id)
                .order_by(AuditLogModel.created_at.asc())
                .all()
            )

            key_actions = ["application_submitted", "applicant_analyzed", "risk_analyzed",
                          "decision_synthesized", "compliance_validated", "notifications_queued"]

            timeline = {}
            for log in audit_logs:
                if log.action in key_actions:
                    timeline[log.action] = log.created_at.isoformat() if log.created_at else None

            # Calculate duration
            if audit_logs:
                start_time = audit_logs[0].created_at
                end_time = audit_logs[-1].created_at
                duration = (end_time - start_time).total_seconds()

                return {
                    "application_id": application_id,
                    "timeline": timeline,
                    "total_duration_seconds": duration,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                }

            return {
                "application_id": application_id,
                "timeline": timeline,
                "total_duration_seconds": 0,
                "start_time": None,
                "end_time": None,
            }

        except Exception as e:
            logger.error(
                f"Error generating workflow timeline: {str(e)}",
                extra={"application_id": application_id},
            )
            raise

    @staticmethod
    def export_audit_log(
        db: Session,
        application_id: str,
        format: str = "json",
    ) -> str:
        """Export audit log for compliance/archival.

        Args:
            db: Database session
            application_id: Application ID
            format: Export format (json, csv)

        Returns:
            Formatted audit log string
        """
        try:
            from database.models import AuditLogModel
            import json
            import csv
            from io import StringIO

            audit_logs = (
                db.query(AuditLogModel)
                .filter_by(application_id=application_id)
                .order_by(AuditLogModel.created_at.asc())
                .all()
            )

            if format == "csv":
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(
                    ["Timestamp", "Action", "Agent", "Details"]
                )

                for log in audit_logs:
                    writer.writerow(
                        [
                            log.created_at.isoformat() if log.created_at else "",
                            log.action,
                            log.agent_name or "",
                            json.dumps(log.details) if log.details else "",
                        ]
                    )

                return output.getvalue()

            else:  # JSON format
                data = [
                    {
                        "timestamp": log.created_at.isoformat() if log.created_at else None,
                        "action": log.action,
                        "agent": log.agent_name,
                        "details": log.details or {},
                    }
                    for log in audit_logs
                ]

                return json.dumps(data, indent=2)

        except Exception as e:
            logger.error(
                f"Error exporting audit log: {str(e)}",
                extra={"application_id": application_id, "format": format},
            )
            raise

    @staticmethod
    def get_system_audit_summary(
        db: Session,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get system-wide audit summary.

        Args:
            db: Database session
            days: Number of days to include in summary

        Returns:
            Dictionary with system audit statistics
        """
        try:
            from database.models import AuditLogModel
            from sqlalchemy import func

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            query = db.query(AuditLogModel).filter(AuditLogModel.created_at >= cutoff_date)

            # Count actions by type
            action_counts = (
                db.query(AuditLogModel.action, func.count(AuditLogModel.id))
                .filter(AuditLogModel.created_at >= cutoff_date)
                .group_by(AuditLogModel.action)
                .all()
            )

            # Count by agent
            agent_counts = (
                db.query(AuditLogModel.agent_name, func.count(AuditLogModel.id))
                .filter(AuditLogModel.created_at >= cutoff_date)
                .group_by(AuditLogModel.agent_name)
                .all()
            )

            return {
                "period_days": days,
                "start_date": cutoff_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "total_actions": query.count(),
                "actions_by_type": {action: count for action, count in action_counts},
                "actions_by_agent": {
                    agent: count for agent, count in agent_counts
                },
            }

        except Exception as e:
            logger.error(
                f"Error generating system audit summary: {str(e)}",
            )
            raise
