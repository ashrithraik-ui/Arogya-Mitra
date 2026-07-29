"""
ArogyaMitra AI — Voice Agent
Transcribes patient audio, generates AI follow-up, converts response to speech.
"""

import logging
import base64
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.consultation import Consultation
from backend.services.stt_service import stt_service, tts_service
from backend.agents.conversation import conversation_agent
from backend.agents.followup import followup_agent
from backend.services.gemini_service import gemini_service
from backend.config import settings

logger = logging.getLogger(__name__)


class VoiceAgent:
    """
    Handles the full voice interaction pipeline:
    1. Speech-to-text transcription
    2. AI response generation
    3. Follow-up question generation
    4. Text-to-speech synthesis
    5. Conversation persistence
    """

    async def process_voice(
        self,
        db: AsyncSession,
        consultation: Consultation,
        audio_bytes: bytes,
        content_type: str,
    ) -> dict:
        """
        Process a voice audio file end-to-end.

        Args:
            db: Async DB session.
            consultation: The active consultation.
            audio_bytes: Raw audio bytes.
            content_type: Audio MIME type.

        Returns:
            Dict with transcription, AI response, follow-up question, audio path.
        """
        # Step 1: Transcribe audio
        transcription = await stt_service.transcribe(audio_bytes, content_type)
        patient_text = transcription.get("text", "")

        if not patient_text or not transcription.get("success"):
            patient_text = (
                "[Voice not transcribed — please type your symptoms manually.]"
            )

        # Step 2: Append patient turn to conversation
        await conversation_agent.append_turn(
            db, consultation, role="patient", message=patient_text
        )

        # Step 3: Extract follow-up answers from transcribed text
        follow_up_answers = conversation_agent.get_follow_up_answers(consultation)
        history = conversation_agent.get_conversation_history(consultation)
        extracted = followup_agent.extract_structured_answers(
            patient_message=patient_text,
            collected_info=follow_up_answers,
            last_question=history[-2]["message"] if len(history) >= 2 else None,
        )
        for key, value in extracted.items():
            await conversation_agent.update_follow_up_answer(db, consultation, key, value)
        follow_up_answers.update(extracted)

        # Step 4: Generate AI acknowledgement response
        ai_response = await gemini_service.generate_ai_chat_response(
            user_message=patient_text,
            chief_complaint=consultation.chief_complaint or patient_text,
            follow_up_answers=follow_up_answers,
            conversation_history=history,
        )

        # Step 5: Generate follow-up question
        question, is_ready = await followup_agent.generate_next_question(
            chief_complaint=consultation.chief_complaint or patient_text,
            collected_info=follow_up_answers,
            conversation_history=history,
        )

        # Step 6: Compose final response text
        full_response = ai_response
        if question and not is_ready:
            full_response = f"{ai_response}\n\n{question}"

        # Step 7: Append AI turn
        await conversation_agent.append_turn(
            db, consultation, role="ai", message=full_response
        )

        # Step 8: Synthesize audio response
        tts_result = await tts_service.synthesize(full_response)
        audio_b64: str | None = None
        if tts_result.get("success") and tts_result.get("audio_bytes"):
            audio_b64 = base64.b64encode(tts_result["audio_bytes"]).decode("utf-8")

        return {
            "transcribed_text": patient_text,
            "transcription_method": transcription.get("method"),
            "ai_response": ai_response,
            "follow_up_question": question if not is_ready else None,
            "is_summary_ready": is_ready,
            "audio_response_base64": audio_b64,
            "disclaimer": settings.AI_DISCLAIMER,
        }


# Singleton instance
voice_agent = VoiceAgent()
