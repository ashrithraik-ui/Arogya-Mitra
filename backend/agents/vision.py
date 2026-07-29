"""
ArogyaMitra AI — Vision Agent
Coordinates medical image analysis and routes findings to the doctor.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.consultation import Consultation
from backend.services.vision_service import vision_service
from backend.services.timeline_service import timeline_service
from backend.models.timeline import TimelineEventType
from backend.config import settings

logger = logging.getLogger(__name__)


class VisionAgent:
    """
    Processes uploaded medical images:
    1. Sends image to Gemini Vision for observation generation.
    2. Stores observations in the consultation record.
    3. Marks the consultation for doctor review.
    4. Adds a timeline event.
    """

    async def process_image(
        self,
        db: AsyncSession,
        consultation: Consultation,
        image_bytes: bytes,
        mime_type: str,
        file_path: str,
    ) -> dict:
        """
        Analyze a medical image and persist observations.

        Args:
            db: Async DB session.
            consultation: The active consultation.
            image_bytes: Raw image bytes.
            mime_type: Image MIME type.
            file_path: Stored file path.

        Returns:
            Dict with observations, key_findings, disclaimer.
        """
        # Vision analysis
        result = await vision_service.analyze_image(image_bytes, mime_type)

        # Persist to consultation
        existing = consultation.vision_observations or ""
        consultation.vision_observations = (
            f"{existing}\n\n--- New Image Analysis ---\n{result['observations']}".strip()
        )
        await db.flush()

        # Timeline event
        await timeline_service.add_event(
            db=db,
            patient_id=consultation.patient_id,
            event_type=TimelineEventType.IMAGE,
            title="Medical Image Uploaded",
            description=(
                f"AI identified {len(result.get('key_findings', []))} observations. "
                "Forwarded to doctor for clinical review."
            ),
            consultation_id=consultation.id,
            file_path=file_path,
            metadata={
                "key_findings": result.get("key_findings", []),
                "forwarded_to_doctor": True,
            },
        )

        logger.info(
            "Vision analysis complete for consultation=%d: findings=%d",
            consultation.id,
            len(result.get("key_findings", [])),
        )

        return {
            "observations": result["observations"],
            "key_findings": result.get("key_findings", []),
            "forwarded_to_doctor": True,
            "disclaimer": settings.AI_DISCLAIMER,
        }


# Singleton instance
vision_agent = VisionAgent()
