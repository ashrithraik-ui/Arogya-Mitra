"""
ArogyaMitra AI — Medical History Agent
Collects and structures patient medical history from conversation.
"""

import logging
from backend.agents.conversation import conversation_agent
from backend.models.consultation import Consultation
from backend.models.patient import Patient
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Fields that constitute a complete medical history profile
MEDICAL_HISTORY_FIELDS = [
    "medical_history",
    "family_history",
    "allergies",
    "current_medications",
    "previous_surgeries",
    "immunization_history",
    "lifestyle",
]


class MedicalHistoryAgent:
    """
    Extracts and organises patient medical history from the consultation.

    Also updates the patient's persistent profile with newly discovered
    allergies, conditions, or medications if they are not already recorded.
    """

    def build_history_summary(self, follow_up_answers: dict) -> str:
        """
        Build a formatted medical history block from collected answers.

        Args:
            follow_up_answers: Dict of collected follow-up information.

        Returns:
            Formatted string suitable for inclusion in AI prompts.
        """
        lines = ["=== MEDICAL HISTORY ==="]
        for field in MEDICAL_HISTORY_FIELDS:
            value = follow_up_answers.get(field)
            if value:
                label = field.replace("_", " ").title()
                lines.append(f"  {label}: {value}")

        if len(lines) == 1:
            lines.append("  No detailed medical history collected yet.")

        return "\n".join(lines)

    def get_missing_history_fields(self, follow_up_answers: dict) -> list[str]:
        """
        Return the list of history fields not yet collected.

        Args:
            follow_up_answers: Already-collected information.

        Returns:
            List of field name strings.
        """
        return [
            field for field in MEDICAL_HISTORY_FIELDS
            if field not in follow_up_answers
        ]

    async def update_patient_profile(
        self,
        db: AsyncSession,
        patient: Patient,
        follow_up_answers: dict,
    ) -> None:
        """
        Update the patient's persistent profile with newly collected information.
        Only updates fields that were empty/None before.

        Args:
            db: Async DB session.
            patient: Patient record to update.
            follow_up_answers: Answers collected during this consultation.
        """
        updated = False

        if not patient.allergies and follow_up_answers.get("allergies"):
            patient.allergies = follow_up_answers["allergies"]
            updated = True

        if not patient.known_conditions and follow_up_answers.get("medical_history"):
            patient.known_conditions = follow_up_answers["medical_history"]
            updated = True

        if not patient.current_medications and follow_up_answers.get("current_medications"):
            patient.current_medications = follow_up_answers["current_medications"]
            updated = True

        if updated:
            await db.flush()
            logger.info("Patient profile updated from consultation: patient_id=%d", patient.id)


# Singleton instance
medical_history_agent = MedicalHistoryAgent()
