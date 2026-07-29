"""
ArogyaMitra AI — Doctor Routing Agent
Routes completed consultations to the most appropriate available doctor.
Falls back to any available doctor if none match the preferred specialization.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.consultation import Consultation, ConsultationStatus
from backend.models.doctor import Doctor
from backend.services.doctor_service import doctor_service
from backend.services.timeline_service import timeline_service
from backend.models.timeline import TimelineEventType

logger = logging.getLogger(__name__)

# Simple keyword → specialization mapping for intelligent routing
SYMPTOM_SPECIALIZATION_MAP = {
    "chest pain": "Cardiologist",
    "heart": "Cardiologist",
    "skin": "Dermatologist",
    "rash": "Dermatologist",
    "eye": "Ophthalmologist",
    "vision": "Ophthalmologist",
    "ear": "ENT",
    "nose": "ENT",
    "throat": "ENT",
    "bone": "Orthopedic",
    "joint": "Orthopedic",
    "fracture": "Orthopedic",
    "mental": "Psychiatrist",
    "anxiety": "Psychiatrist",
    "depression": "Psychiatrist",
    "child": "Pediatrician",
    "pregnancy": "Gynecologist",
    "diabetes": "Endocrinologist",
    "thyroid": "Endocrinologist",
    "kidney": "Nephrologist",
    "urine": "Nephrologist",
    "liver": "Gastroenterologist",
    "stomach": "Gastroenterologist",
}


class DoctorRoutingAgent:
    """
    Intelligently routes a consultation to the best available doctor.

    Routing priority:
    1. Specialty match based on chief complaint keywords
    2. Any available active doctor
    3. Returns None if no doctors are available (consultation stays pending)
    """

    def _infer_specialization(self, chief_complaint: str) -> str | None:
        """
        Infer a preferred medical specialization from the chief complaint text.

        Args:
            chief_complaint: Patient's chief complaint string.

        Returns:
            Specialization string or None.
        """
        if not chief_complaint:
            return None

        complaint_lower = chief_complaint.lower()
        for keyword, specialization in SYMPTOM_SPECIALIZATION_MAP.items():
            if keyword in complaint_lower:
                return specialization

        return None  # Default to "General Physician" routing in service

    async def route_consultation(
        self,
        db: AsyncSession,
        consultation: Consultation,
    ) -> Doctor | None:
        """
        Assign the most suitable available doctor to a consultation.

        Args:
            db: Async DB session.
            consultation: The consultation to route.

        Returns:
            Assigned Doctor or None if no doctor is available.
        """
        preferred_specialization = self._infer_specialization(
            consultation.chief_complaint or ""
        )

        doctor = await doctor_service.find_available_doctor(
            db,
            specialization=preferred_specialization,
        )

        if doctor:
            consultation.doctor_id = doctor.id
            consultation.status = ConsultationStatus.ASSIGNED
            await db.flush()

            # Add timeline event
            await timeline_service.add_event(
                db=db,
                patient_id=consultation.patient_id,
                event_type=TimelineEventType.CONSULTATION,
                title="Doctor Assigned",
                description=f"Dr. {doctor.name} ({doctor.specialization}) assigned to your consultation.",
                consultation_id=consultation.id,
                metadata={"doctor_id": doctor.id, "doctor_name": doctor.name},
            )

            logger.info(
                "Consultation %d assigned to doctor %d (%s).",
                consultation.id,
                doctor.id,
                doctor.name,
            )
        else:
            logger.warning(
                "No available doctor found for consultation %d. Stays pending.",
                consultation.id,
            )

        return doctor


# Singleton instance
doctor_routing_agent = DoctorRoutingAgent()
