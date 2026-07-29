"""
ArogyaMitra AI — Health Timeline Service
Creates and retrieves chronological health events for a patient.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.timeline import HealthTimeline, TimelineEventType
from backend.utils.helpers import safe_json_dumps

logger = logging.getLogger(__name__)


class TimelineService:
    """Manages the patient health timeline."""

    async def add_event(
        self,
        db: AsyncSession,
        patient_id: int,
        event_type: TimelineEventType,
        title: str,
        description: str | None = None,
        metadata: dict | None = None,
        consultation_id: int | None = None,
        file_path: str | None = None,
        event_date: datetime | None = None,
    ) -> HealthTimeline:
        """
        Append a new event to the patient's health timeline.

        Args:
            db: Async DB session.
            patient_id: Owner of the timeline event.
            event_type: Category of the event.
            title: Short human-readable title.
            description: Optional longer description.
            metadata: Optional extra data (serialised to JSON).
            consultation_id: Link to a consultation if applicable.
            file_path: Path to an associated uploaded file.
            event_date: Clinical date; defaults to now.

        Returns:
            Persisted HealthTimeline instance.
        """
        event = HealthTimeline(
            patient_id=patient_id,
            event_type=event_type,
            title=title,
            description=description,
            metadata_json=safe_json_dumps(metadata or {}),
            consultation_id=consultation_id,
            file_path=file_path,
            event_date=event_date or datetime.now(timezone.utc),
        )
        db.add(event)
        await db.flush()
        logger.info(
            "Timeline event added: patient=%d type=%s title=%r",
            patient_id, event_type, title,
        )
        return event

    async def get_patient_timeline(
        self,
        db: AsyncSession,
        patient_id: int,
        event_type: TimelineEventType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[HealthTimeline]:
        """
        Retrieve a patient's health timeline, newest first.

        Args:
            db: Async DB session.
            patient_id: Target patient.
            event_type: Optional filter by event type.
            limit: Maximum number of events to return.
            offset: Pagination offset.

        Returns:
            List of HealthTimeline instances.
        """
        query = select(HealthTimeline).where(
            HealthTimeline.patient_id == patient_id
        )
        if event_type:
            query = query.where(HealthTimeline.event_type == event_type)

        query = query.order_by(HealthTimeline.event_date.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_event_count(self, db: AsyncSession, patient_id: int) -> int:
        """Return the total number of timeline events for a patient."""
        from sqlalchemy import func
        result = await db.execute(
            select(func.count()).where(HealthTimeline.patient_id == patient_id)
        )
        return result.scalar() or 0


# Singleton instance
timeline_service = TimelineService()
