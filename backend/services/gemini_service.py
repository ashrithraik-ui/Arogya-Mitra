"""
ArogyaMitra AI — Gemini AI Service
Provides conversation, summarisation, vision, and structured-output capabilities.
Uses the new google-genai SDK (google.genai).
Gracefully degrades when the API key is not configured.
"""

import asyncio
import logging
import os
from typing import Optional

from backend.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Wrapper around the new Google GenAI SDK (google.genai).

    When GEMINI_API_KEY is not set the service returns clearly labelled
    fallback responses so the rest of the application remains functional
    for development and testing.
    """

    def __init__(self) -> None:
        self._client = None
        self._configured = False
        self._init_client()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init_client(self) -> None:
        """Attempt to initialise the Gemini SDK."""
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning(
                "GEMINI_API_KEY is not configured. "
                "Set the key in your .env file to enable Gemini."
            )
            return

        try:
            from google import genai  # type: ignore
            self._client = genai.Client(api_key=api_key)
            self._configured = True
            logger.info("Gemini AI client initialised successfully (google-genai SDK).")
        except ImportError:
            logger.error("google-genai package not installed. Run: pip install google-genai")
        except Exception as exc:
            logger.error("Failed to initialise Gemini client: %s", exc)

    async def _generate(self, prompt: str, temperature: float | None = None) -> str:
        """Send a text prompt to Gemini and return the response text."""
        if not self._configured or self._client is None:
            self._init_client()

        if not self._configured or self._client is None:
            return ""

        try:
            from google.genai import types  # type: ignore

            config = types.GenerateContentConfig(
                temperature=temperature or settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS,
            )

            def _call():
                response = self._client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=config,
                )
                return response.text.strip() if response and response.text else ""

            return await asyncio.to_thread(_call)
        except Exception as exc:
            logger.error("Gemini text generation failed: %s", exc)
            return ""

    # ── Public API ────────────────────────────────────────────────────────────

    async def get_follow_up_question(
        self,
        chief_complaint: str,
        collected_info: dict,
        conversation_history: list[dict],
    ) -> str:
        """
        Generate the next dynamic follow-up question based on what we know so far.
        Returns an empty string when enough information has been collected.
        """
        already_asked = list(collected_info.keys())
        history_text = "\n".join(
            f"  {t['role'].upper()}: {t['message']}" for t in conversation_history[-6:]
        )

        prompt = f"""
You are a medical AI assistant helping collect patient information before a doctor consultation.
Your ONLY job is to ask ONE clear, empathetic follow-up question to gather missing clinical information.

IMPORTANT RULES:
- You do NOT diagnose, prescribe, or assess risk.
- Ask ONE question at a time.
- Be empathetic, simple, and in plain language.
- If all key areas are covered, respond with exactly: SUMMARY_READY

Chief Complaint: {chief_complaint}

Information already collected: {', '.join(already_asked) if already_asked else 'None yet'}

Key areas to cover (in order of priority):
1. Duration and onset of symptoms
2. Severity (scale 1-10)
3. Associated symptoms
4. Current medications
5. Known allergies
6. Previous medical history
7. Family history (if relevant)
8. Lifestyle factors (smoking, alcohol, diet)
9. Any uploaded reports or images to share

Recent conversation:
{history_text if history_text else '  [No conversation yet]'}

Generate the next single follow-up question. If all key areas are adequately covered, reply: SUMMARY_READY
"""
        result = await self._generate(prompt, temperature=0.6)
        if result and result.strip():
            return result.strip()

        # Fallback question sequence if Gemini returns empty or API quota exceeded
        msg_count = len(conversation_history)
        if msg_count <= 2:
            return "How long have you been experiencing these symptoms, and did they start suddenly or gradually?"
        elif msg_count <= 4:
            return "On a scale of 1 to 10, how severe is your pain or discomfort right now?"
        elif msg_count <= 6:
            return "Are you currently taking any medications or do you have any known allergies?"
        else:
            return "SUMMARY_READY"

    async def generate_patient_summary(
        self,
        patient_info: dict,
        chief_complaint: str,
        follow_up_answers: dict,
        ocr_text: str | None = None,
        vision_observations: str | None = None,
    ) -> str:
        """
        Generate a structured patient summary for the doctor.
        Includes a mandatory AI safety disclaimer.
        """
        ocr_section = f"\nExtracted Report Text:\n{ocr_text}" if ocr_text else ""
        vision_section = f"\nMedical Image Observations:\n{vision_observations}" if vision_observations else ""

        prompt = f"""
You are an AI medical assistant preparing a structured patient summary for a doctor.

CRITICAL RULES:
- You do NOT diagnose.
- You do NOT prescribe.
- You do NOT assess risk levels.
- You ONLY organise and present the information the patient provided.

Patient Information:
  Name: {patient_info.get('name', 'Unknown')}
  Age: {patient_info.get('age', 'Not provided')}
  Gender: {patient_info.get('gender', 'Not provided')}
  Blood Group: {patient_info.get('blood_group', 'Not provided')}
  Known Allergies: {patient_info.get('allergies', 'None reported')}
  Known Conditions: {patient_info.get('known_conditions', 'None reported')}
  Current Medications: {patient_info.get('current_medications', 'None reported')}

Chief Complaint: {chief_complaint}

Follow-up Information Collected:
{chr(10).join(f'  {k.replace("_", " ").title()}: {v}' for k, v in follow_up_answers.items() if v)}
{ocr_section}
{vision_section}

Generate a structured clinical summary using these sections:
1. Chief Complaint
2. Symptom Description (duration, severity, character)
3. Associated Symptoms
4. Relevant Medical History
5. Current Medications & Allergies
6. Uploaded Findings (if any)
7. Patient-Reported Lifestyle Factors
8. Information for Doctor's Review

End with: "⚠️ {settings.AI_DISCLAIMER}"
"""
        return await self._generate(prompt, temperature=0.4)

    async def explain_medical_report(self, extracted_text: str) -> tuple[str, list[str]]:
        """
        Explain a medical report in simple language and extract key findings.
        Returns (explanation, key_findings_list).
        """
        prompt = f"""
You are an AI assistant helping a patient understand their medical report.

RULES:
- Explain in simple, clear language a non-medical person can understand.
- Do NOT diagnose or recommend treatments.
- Highlight abnormal values but state that the doctor will interpret them.
- Be reassuring and calm in tone.

Medical Report Text:
{extracted_text[:3000]}

Provide:
1. A clear, simple explanation of what this report shows.
2. A list of KEY FINDINGS (prefix each with "KEY_FINDING: ").

End with: "Your doctor will review this report and explain what it means for your health."
"""
        response = await self._generate(prompt, temperature=0.5)

        # Extract key findings from the response
        key_findings = []
        explanation_lines = []
        for line in response.split("\n"):
            if line.startswith("KEY_FINDING:"):
                key_findings.append(line.replace("KEY_FINDING:", "").strip())
            else:
                explanation_lines.append(line)

        return "\n".join(explanation_lines).strip(), key_findings

    async def analyze_medical_image(
        self, image_bytes: bytes, mime_type: str
    ) -> tuple[str, list[str]]:
        """
        Analyze a medical image and generate clinical observations.
        Returns (observations_text, key_findings_list).
        """
        prompt = """
You are an AI assistant providing preliminary medical image observations for a doctor.

CRITICAL RULES:
- You do NOT diagnose.
- You do NOT assess severity or risk.
- You ONLY describe visible features for the doctor's review.
- State clearly these are AI-generated observations, not a clinical diagnosis.

Please describe:
1. What type of medical image this appears to be.
2. General visible features and structure.
3. Any notable observations (prefix each with "OBSERVATION: ").

End with: "⚠️ These are AI-generated preliminary observations. The treating physician must review and interpret this image. The AI does not diagnose or assess risk."
"""
        response = await self._generate_vision(prompt, image_bytes, mime_type)

        observations = []
        description_lines = []
        for line in response.split("\n"):
            if line.startswith("OBSERVATION:"):
                observations.append(line.replace("OBSERVATION:", "").strip())
            else:
                description_lines.append(line)

        return "\n".join(description_lines).strip(), observations

    async def generate_ai_chat_response(
        self,
        user_message: str,
        chief_complaint: str,
        follow_up_answers: dict,
        conversation_history: list[dict],
    ) -> str:
        """Generate a conversational AI response acknowledging the patient's input."""
        history_text = "\n".join(
            f"  {t['role'].upper()}: {t['message']}" for t in conversation_history[-4:]
        )

        prompt = f"""
You are ArogyaMitra, a compassionate AI healthcare assistant preparing patients for a doctor consultation.

CRITICAL RULES:
- You do NOT diagnose, prescribe, or assess risk.
- You collect information to help the doctor.
- Be warm, clear, and reassuring.
- Acknowledge what the patient said before asking anything else.
- Keep responses concise (2-3 sentences max).

Chief Complaint: {chief_complaint}
Collected so far: {list(follow_up_answers.keys())}

Recent conversation:
{history_text if history_text else '  [Start of conversation]'}

Patient just said: "{user_message}"

Acknowledge their message briefly and warmly (1-2 sentences). Do not ask a question here.
"""
        res = await self._generate(prompt, temperature=0.7)
        if res and res.strip():
            return res.strip()
        return "Thank you for sharing those details."

    @property
    def is_configured(self) -> bool:
        """True if the Gemini client is ready to use."""
        return self._configured


# Singleton instance shared across all agents
gemini_service = GeminiService()
