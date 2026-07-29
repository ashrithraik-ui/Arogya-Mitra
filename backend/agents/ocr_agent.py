"""
ArogyaMitra AI — OCR Agent
Coordinates OCR extraction and AI-powered report explanation.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.consultation import Consultation
from backend.services.ocr_service import ocr_service
from backend.services.gemini_service import gemini_service
from backend.services.timeline_service import timeline_service
from backend.models.timeline import TimelineEventType
from backend.config import settings

logger = logging.getLogger(__name__)


class OCRAgent:
    """
    Processes uploaded medical reports (PDFs and images):
    1. Extracts raw text via OCR.
    2. Sends extracted text to Gemini for plain-language explanation.
    3. Stores the text in the consultation record.
    4. Adds a timeline event.
    """

    async def process_report(
        self,
        db: AsyncSession,
        consultation: Consultation,
        file_bytes: bytes,
        content_type: str,
        file_path: str,
    ) -> dict:
        """
        Extract and explain a medical report.

        Args:
            db: Async DB session.
            consultation: The active consultation.
            file_bytes: Raw file bytes.
            content_type: MIME type.
            file_path: Stored file path (for timeline).

        Returns:
            Dict with extracted_text, explanation, key_findings, disclaimer.
        """
        # Step 1: OCR extraction
        ocr_result = await ocr_service.extract_text_from_file(file_bytes, content_type)
        extracted_text = ocr_result.get("extracted_text", "")

        # Step 2: AI explanation
        explanation = ""
        key_findings: list[str] = []
        if extracted_text and not extracted_text.startswith("["):
            explanation, key_findings = await gemini_service.explain_medical_report(
                extracted_text
            )
        else:
            explanation = (
                "The report text could not be extracted automatically. "
                "The file has been stored and will be reviewed by your doctor."
            )

        # Step 3: Persist to consultation
        existing = consultation.ocr_extracted_text or ""
        consultation.ocr_extracted_text = (
            f"{existing}\n\n--- New Report ---\n{extracted_text}".strip()
        )
        await db.flush()

        # Step 4: Timeline event
        await timeline_service.add_event(
            db=db,
            patient_id=consultation.patient_id,
            event_type=TimelineEventType.REPORT,
            title="Medical Report Uploaded",
            description=f"Report processed. {len(key_findings)} key findings identified.",
            consultation_id=consultation.id,
            file_path=file_path,
            metadata={"key_findings_count": len(key_findings), "method": ocr_result.get("method")},
        )

        logger.info(
            "OCR processed for consultation=%d: method=%s success=%s",
            consultation.id,
            ocr_result.get("method"),
            ocr_result.get("success"),
        )

        return {
            "extracted_text": extracted_text,
            "explanation": explanation,
            "key_findings": key_findings,
            "disclaimer": settings.AI_DISCLAIMER,
            "ocr_method": ocr_result.get("method"),
        }


# Singleton instance
ocr_agent = OCRAgent()
