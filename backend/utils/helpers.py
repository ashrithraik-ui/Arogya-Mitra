"""
ArogyaMitra AI — General Utility Helpers
"""

import json
import re
from datetime import datetime, timezone
from typing import Any


def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def safe_json_loads(value: str | None, default: Any = None) -> Any:
    """
    Parse a JSON string, returning `default` on any error.

    Args:
        value: JSON string to parse.
        default: Value to return when parsing fails (default: None).
    """
    if value is None:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(value: Any) -> str:
    """
    Serialize an object to a JSON string, handling non-serializable types.

    Returns:
        JSON string, or "{}" / "[]" fallback on failure.
    """
    try:
        return json.dumps(value, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return "null"


def sanitize_text(text: str) -> str:
    """
    Remove control characters and excessive whitespace from a string.
    Safe to use on patient input before passing to AI.
    """
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\s{3,}", "  ", text)
    return text.strip()


def truncate_text(text: str, max_chars: int = 1000) -> str:
    """Truncate text to max_chars, appending '…' if truncated."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def build_patient_context_prompt(
    chief_complaint: str,
    follow_up_answers: dict,
    conversation_history: list[dict],
) -> str:
    """
    Build a structured context string from patient data for Gemini prompts.
    Includes chief complaint, collected answers, and recent conversation.
    """
    lines = ["=== PATIENT CONTEXT ===", f"Chief Complaint: {chief_complaint}"]

    if follow_up_answers:
        lines.append("\n--- Collected Information ---")
        for key, value in follow_up_answers.items():
            if value:
                lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    if conversation_history:
        lines.append("\n--- Recent Conversation (last 6 exchanges) ---")
        for turn in conversation_history[-6:]:
            role = turn.get("role", "unknown").upper()
            msg = truncate_text(turn.get("message", ""), 300)
            lines.append(f"  {role}: {msg}")

    return "\n".join(lines)
