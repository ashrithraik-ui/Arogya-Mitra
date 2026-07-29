"""
ArogyaMitra AI — Summary Agent
Generates structured patient summaries for doctor review.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.consultation import Consultation
from backend.models.patient import Patient
from backend.services.gemini_service import gemini_service
from backend.agents.conversation import conversation_agent
from backend.config import settings

logger = logging.getLogger(__name__)


class SummaryAgent:
    """
    Generates AI-powered patient summaries.

    The summary is structured for quick clinical review by the doctor.
    It contains NO diagnosis, NO risk assessment, and NO treatment recommendation.
    The AI is an information organiser — the doctor is the decision-maker.
    """

    async def generate_summary(
        self,
        db: AsyncSession,
        consultation: Consultation,
        patient: Patient,
    ) -> str:
        """
        Generate and persist a structured patient summary.

        Args:
            db: Async DB session.
            consultation: The active consultation.
            patient: The patient being summarised.

        Returns:
            Generated summary text (also stored in consultation.ai_summary).
        """
        follow_up_answers = conversation_agent.get_follow_up_answers(consultation)

        patient_info = {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "allergies": patient.allergies,
            "known_conditions": patient.known_conditions,
            "current_medications": patient.current_medications,
        }

        summary = await gemini_service.generate_patient_summary(
            patient_info=patient_info,
            chief_complaint=consultation.chief_complaint or "Not specified",
            follow_up_answers=follow_up_answers,
            ocr_text=consultation.ocr_extracted_text,
            vision_observations=consultation.vision_observations,
        )

        consultation.ai_summary = summary
        await db.flush()

        logger.info(
            "AI summary generated for consultation=%d patient=%d",
            consultation.id,
            patient.id,
        )
        return summary

    def is_ready_for_summary(self, follow_up_answers: dict) -> bool:
        """
        Determine whether enough information has been collected to generate a summary.
        Minimum required: chief complaint + at least 3 follow-up answers.
        """
        minimum_keys = {"duration", "severity", "current_medications"}
        return minimum_keys.issubset(follow_up_answers.keys())


# Singleton instance
summary_agent = SummaryAgent()
