"""
ArogyaMitra AI — Orchestrator Agent
The central coordinator that routes requests through the appropriate agent pipeline.

Pipeline:
  Patient message
      → ConversationAgent (session management)
      → FollowUpAgent (next question generation + answer extraction)
      → MedicalHistoryAgent (profile update)
      → SummaryAgent (when enough info collected)
      → DoctorRoutingAgent (assign doctor when summary ready)
      → TimelineAgent (record milestones)
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.consultation import Consultation
from backend.models.patient import Patient
from backend.agents.conversation import conversation_agent
from backend.agents.followup import followup_agent
from backend.agents.medical_history import medical_history_agent
from backend.agents.summary import summary_agent
from backend.agents.doctor_routing import doctor_routing_agent
from backend.agents.timeline import timeline_agent
from backend.services.gemini_service import gemini_service
from backend.config import settings

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Top-level agent that coordinates the full patient consultation pipeline.

    Entry point for:
    - Patient chat messages (POST /patient/chat)
    - Each turn runs through: conversation → follow-up → history → summary → routing
    """

    async def handle_chat(
        self,
        db: AsyncSession,
        patient_id: int,
        consultation_id: int | None,
        message: str,
    ) -> dict:
        """
        Process one patient chat message through the full agent pipeline.

        Args:
            db: Async DB session.
            patient_id: ID of the patient sending the message.
            consultation_id: Existing consultation (None → create new).
            message: Patient's text input.

        Returns:
            Dict with consultation_id, ai_response, follow_up_question,
            is_summary_ready, disclaimer.
        """
        # ── 1. Load patient ────────────────────────────────────────────────────
        patient_result = await db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = patient_result.scalars().first()
        if not patient:
            raise ValueError(f"Patient with id={patient_id} not found.")

        # ── 2. Get or create consultation ──────────────────────────────────────
        consultation = await conversation_agent.get_or_create_consultation(
            db=db,
            patient_id=patient_id,
            consultation_id=consultation_id,
            chief_complaint=message,
        )
        is_new = consultation_id is None

        # ── 3. Record consultation start on first message ──────────────────────
        if is_new:
            await timeline_agent.record_consultation_start(
                db=db,
                patient_id=patient_id,
                consultation_id=consultation.id,
                chief_complaint=message[:200],
            )

        # ── 4. Append patient turn ─────────────────────────────────────────────
        await conversation_agent.append_turn(db, consultation, role="patient", message=message)

        # ── 5. Extract structured answers from message ─────────────────────────
        history = conversation_agent.get_conversation_history(consultation)
        follow_up_answers = conversation_agent.get_follow_up_answers(consultation)
        last_ai_msg = None
        for turn in reversed(history[:-1]):   # exclude the turn just appended
            if turn["role"] == "ai":
                last_ai_msg = turn["message"]
                break

        extracted = followup_agent.extract_structured_answers(
            patient_message=message,
            collected_info=follow_up_answers,
            last_question=last_ai_msg,
        )
        for key, value in extracted.items():
            await conversation_agent.update_follow_up_answer(db, consultation, key, value)
        follow_up_answers.update(extracted)

        # ── 6. Update patient medical history profile ──────────────────────────
        await medical_history_agent.update_patient_profile(db, patient, follow_up_answers)

        # ── 7. Generate AI acknowledgement ─────────────────────────────────────
        ai_acknowledgement = await gemini_service.generate_ai_chat_response(
            user_message=message,
            chief_complaint=consultation.chief_complaint or message,
            follow_up_answers=follow_up_answers,
            conversation_history=history,
        )
        if not ai_acknowledgement:
            ai_acknowledgement = "Thank you for providing that detail."

        # ── 8. Generate next follow-up question ────────────────────────────────
        follow_up_question, is_summary_ready = await followup_agent.generate_next_question(
            chief_complaint=consultation.chief_complaint or message,
            collected_info=follow_up_answers,
            conversation_history=history,
        )

        # ── 9. Generate summary if ready ───────────────────────────────────────
        if is_summary_ready and not consultation.ai_summary:
            await summary_agent.generate_summary(db, consultation, patient)
            await timeline_agent.record_summary_generated(db, consultation.id, consultation.id)
            await doctor_routing_agent.route_consultation(db, consultation)

        # ── 10. Build final AI response ────────────────────────────────────────
        if is_summary_ready:
            final_response = (
                f"{ai_acknowledgement}\n\n"
                "✅ I have collected all the necessary information. "
                "Your complete health summary has been prepared and sent to a doctor for review. "
                "You will be contacted shortly."
            )
        else:
            final_response = (
                f"{ai_acknowledgement}\n\n{follow_up_question}"
                if follow_up_question
                else ai_acknowledgement
            )

        # ── 11. Append AI turn ─────────────────────────────────────────────────
        await conversation_agent.append_turn(db, consultation, role="ai", message=final_response)

        return {
            "consultation_id": consultation.id,
            "ai_response": ai_acknowledgement,
            "follow_up_question": follow_up_question if not is_summary_ready else None,
            "is_summary_ready": is_summary_ready,
            "disclaimer": settings.AI_DISCLAIMER,
        }


# Singleton instance
orchestrator_agent = OrchestratorAgent()
