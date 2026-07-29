"""
ArogyaMitra AI — Conversation Agent
Manages the patient conversation session: stores turns, retrieves context.
"""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.consultation import Consultation, ConsultationStatus
from backend.models.patient import Patient
from backend.utils.helpers import safe_json_loads, safe_json_dumps

logger = logging.getLogger(__name__)


class ConversationAgent:
    """
    Maintains the conversation state for a patient consultation.

    Responsibilities:
    - Create or resume a consultation session
    - Append turns to conversation history
    - Expose collected follow-up answers
    """

    async def get_or_create_consultation(
        self,
        db: AsyncSession,
        patient_id: int,
        consultation_id: int | None,
        chief_complaint: str,
    ) -> Consultation:
        """
        Return an existing open consultation or create a new one.

        Args:
            db: Async DB session.
            patient_id: Patient who owns this consultation.
            consultation_id: Existing consultation to continue (optional).
            chief_complaint: Patient's chief complaint for new consultations.

        Returns:
            Consultation instance.
        """
        if consultation_id:
            result = await db.execute(
                select(Consultation).where(
                    Consultation.id == consultation_id,
                    Consultation.patient_id == patient_id,
                )
            )
            consultation = result.scalars().first()
            if consultation:
                return consultation
            logger.warning(
                "Consultation %d not found for patient %d — creating new one.",
                consultation_id,
                patient_id,
            )

        consultation = Consultation(
            patient_id=patient_id,
            status=ConsultationStatus.PENDING,
            chief_complaint=chief_complaint,
            conversation_history="[]",
            follow_up_answers="{}",
            uploaded_files="[]",
        )
        db.add(consultation)
        await db.flush()
        logger.info("New consultation created: id=%d patient=%d", consultation.id, patient_id)
        return consultation

    def get_conversation_history(self, consultation: Consultation) -> list[dict]:
        """Deserialise conversation history from the DB column."""
        return safe_json_loads(consultation.conversation_history, default=[])

    def get_follow_up_answers(self, consultation: Consultation) -> dict:
        """Deserialise collected follow-up answers from the DB column."""
        return safe_json_loads(consultation.follow_up_answers, default={})

    def get_uploaded_files(self, consultation: Consultation) -> list[str]:
        """Deserialise uploaded file paths from the DB column."""
        return safe_json_loads(consultation.uploaded_files, default=[])

    async def append_turn(
        self,
        db: AsyncSession,
        consultation: Consultation,
        role: str,
        message: str,
    ) -> None:
        """
        Add a new conversation turn and persist it.

        Args:
            db: Async DB session.
            consultation: Consultation to update.
            role: 'patient' or 'ai'.
            message: Text content of the turn.
        """
        history = self.get_conversation_history(consultation)
        history.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        consultation.conversation_history = safe_json_dumps(history)
        await db.flush()

    async def update_follow_up_answer(
        self,
        db: AsyncSession,
        consultation: Consultation,
        key: str,
        value: str,
    ) -> None:
        """
        Store a follow-up answer (e.g. duration='3 days') in the consultation.

        Args:
            db: Async DB session.
            consultation: Consultation to update.
            key: Answer category key (e.g. 'duration', 'severity').
            value: Answer value.
        """
        answers = self.get_follow_up_answers(consultation)
        answers[key] = value
        consultation.follow_up_answers = safe_json_dumps(answers)
        await db.flush()

    async def add_uploaded_file(
        self,
        db: AsyncSession,
        consultation: Consultation,
        file_path: str,
    ) -> None:
        """Append a file path to the consultation's uploaded files list."""
        files = self.get_uploaded_files(consultation)
        if file_path not in files:
            files.append(file_path)
            consultation.uploaded_files = safe_json_dumps(files)
            await db.flush()


# Singleton instance
conversation_agent = ConversationAgent()
