"""
ArogyaMitra AI — Follow-up Question Agent
Generates dynamic follow-up questions to fill information gaps.
Extracts structured answers from patient responses.
"""

import re
import logging
from backend.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

# Patterns used to extract structured information from free-text responses
EXTRACTION_PATTERNS = {
    "duration": [
        r"\b(\d+)\s*(day|days|week|weeks|month|months|hour|hours)\b",
        r"\bsince\s+(\w+)",
        r"\bfor\s+(?:the\s+)?(?:past\s+)?(\d+\s+\w+)",
    ],
    "severity": [
        r"\b([1-9]|10)\s*(?:out of|\/)\s*10\b",
        r"\b(mild|moderate|severe|very severe|unbearable|slight|extreme)\b",
    ],
    "allergies": [
        r"\ballerg(?:ic|y|ies)\s+to\s+([\w\s,]+)",
        r"\bno\s+(?:known\s+)?allerg",
        r"\bnkda\b",
    ],
}


class FollowUpAgent:
    """
    Manages the follow-up question cycle.

    Generates the next contextual question and attempts to extract
    structured information from the patient's free-text responses.
    """

    async def generate_next_question(
        self,
        chief_complaint: str,
        collected_info: dict,
        conversation_history: list[dict],
    ) -> tuple[str, bool]:
        """
        Generate the next follow-up question.

        Args:
            chief_complaint: Patient's initial complaint.
            collected_info: Information already gathered.
            conversation_history: Full conversation so far.

        Returns:
            Tuple of (question_text, is_summary_ready).
            is_summary_ready is True when all key areas are covered.
        """
        response = await gemini_service.get_follow_up_question(
            chief_complaint=chief_complaint,
            collected_info=collected_info,
            conversation_history=conversation_history,
        )

        if "SUMMARY_READY" in response.upper():
            return "", True

        # If Gemini is not configured or returns an empty string, use rule-based fallback
        if not response.strip():
            question = self._rule_based_question(collected_info)
            return question, False

        return response.strip(), False

    def _rule_based_question(self, collected_info: dict) -> str:
        """
        Rule-based fallback question sequence when AI is unavailable.
        Asks questions in clinical priority order.
        """
        question_map = [
            ("duration", "How long have you been experiencing these symptoms?"),
            ("severity", "On a scale of 1 to 10, how severe are your symptoms?"),
            ("associated_symptoms", "Do you have any other symptoms along with this?"),
            ("current_medications", "Are you currently taking any medicines?"),
            ("allergies", "Do you have any known drug or food allergies?"),
            ("medical_history", "Do you have any existing medical conditions like diabetes, hypertension, or heart disease?"),
            ("lifestyle", "Do you smoke, consume alcohol, or have any special dietary habits?"),
            ("family_history", "Is there any family history of similar conditions?"),
        ]

        for key, question in question_map:
            if key not in collected_info:
                return question

        return "Is there anything else you would like to tell your doctor?"

    def extract_structured_answers(
        self,
        patient_message: str,
        collected_info: dict,
        last_question: str | None = None,
    ) -> dict:
        """
        Attempt to extract structured key-value pairs from a patient's free-text response.
        Uses regex patterns and context from the last question asked.

        Args:
            patient_message: The patient's latest message.
            collected_info: Already-collected information.
            last_question: The question that prompted this response.

        Returns:
            Dict of newly extracted key-value pairs to merge into collected_info.
        """
        extracted: dict = {}
        message_lower = patient_message.lower()

        # Duration detection
        if "duration" not in collected_info:
            for pattern in EXTRACTION_PATTERNS["duration"]:
                match = re.search(pattern, message_lower)
                if match:
                    extracted["duration"] = match.group(0).strip()
                    break

        # Severity detection
        if "severity" not in collected_info:
            for pattern in EXTRACTION_PATTERNS["severity"]:
                match = re.search(pattern, message_lower)
                if match:
                    extracted["severity"] = match.group(0).strip()
                    break

        # Allergy detection
        if "allergies" not in collected_info:
            for pattern in EXTRACTION_PATTERNS["allergies"]:
                match = re.search(pattern, message_lower)
                if match:
                    extracted["allergies"] = (
                        "None known" if "no" in match.group(0) or "nkda" in match.group(0)
                        else match.group(1).strip() if match.lastindex else match.group(0)
                    )
                    break

        # Context-based extraction from last question
        if last_question:
            q_lower = last_question.lower()
            if "medication" in q_lower and "current_medications" not in collected_info:
                extracted["current_medications"] = patient_message.strip()
            elif "lifestyle" in q_lower and "lifestyle" not in collected_info:
                extracted["lifestyle"] = patient_message.strip()
            elif "family" in q_lower and "family_history" not in collected_info:
                extracted["family_history"] = patient_message.strip()
            elif "medical condition" in q_lower and "medical_history" not in collected_info:
                extracted["medical_history"] = patient_message.strip()
            elif "other symptom" in q_lower and "associated_symptoms" not in collected_info:
                extracted["associated_symptoms"] = patient_message.strip()

        return extracted


# Singleton instance
followup_agent = FollowUpAgent()
