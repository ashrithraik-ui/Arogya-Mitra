"""
ArogyaMitra AI — Timeline Agent
Adds timeline events at key milestones in the consultation lifecycle.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.timeline_service import timeline_service
from backend.models.timeline import TimelineEventType

logger = logging.getLogger(__name__)


class TimelineAgent:
    """
    Creates structured health timeline entries at clinical milestones.
    Called by the Orchestrator Agent at each major consultation step.
    """

    async def record_consultation_start(
        self,
        db: AsyncSession,
        patient_id: int,
        consultation_id: int,
        chief_complaint: str,
    ) -> None:
        """Record the start of a new consultation session."""
        await timeline_service.add_event(
            db=db,
            patient_id=patient_id,
            event_type=TimelineEventType.CONSULTATION,
            title="Consultation Started",
            description=f"Chief complaint: {chief_complaint}",
            consultation_id=consultation_id,
        )

    async def record_summary_generated(
        self,
        db: AsyncSession,
        patient_id: int,
        consultation_id: int,
    ) -> None:
        """Record when the AI summary was generated and sent to a doctor."""
        await timeline_service.add_event(
            db=db,
            patient_id=patient_id,
            event_type=TimelineEventType.CONSULTATION,
            title="AI Summary Generated",
            description="Patient summary prepared and forwarded for doctor review.",
            consultation_id=consultation_id,
        )

    async def record_prescription(
        self,
        db: AsyncSession,
        patient_id: int,
        consultation_id: int,
        doctor_name: str,
        diagnosis: str,
    ) -> None:
        """Record when a doctor issues a prescription."""
        await timeline_service.add_event(
            db=db,
            patient_id=patient_id,
            event_type=TimelineEventType.PRESCRIPTION,
            title="Prescription Issued",
            description=f"Dr. {doctor_name} — Diagnosis: {diagnosis}",
            consultation_id=consultation_id,
            metadata={"doctor": doctor_name, "diagnosis": diagnosis},
        )

    async def record_referral(
        self,
        db: AsyncSession,
        patient_id: int,
        consultation_id: int,
        hospital: str,
        doctor_name: str,
    ) -> None:
        """Record a hospital or specialist referral."""
        await timeline_service.add_event(
            db=db,
            patient_id=patient_id,
            event_type=TimelineEventType.REFERRAL,
            title="Hospital Referral",
            description=f"Referred to {hospital} by Dr. {doctor_name}.",
            consultation_id=consultation_id,
            metadata={"hospital": hospital, "doctor": doctor_name},
        )


# Singleton instance
timeline_agent = TimelineAgent()
