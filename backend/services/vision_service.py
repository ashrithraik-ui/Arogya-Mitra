"""
ArogyaMitra AI — Medical Vision Service
Wraps the Gemini Vision analysis and adds medical-context safety layers.
"""

import logging
from backend.services.gemini_service import gemini_service
from backend.config import settings

logger = logging.getLogger(__name__)


class VisionService:
    """
    Analyzes medical images and generates preliminary observations for doctor review.

    IMPORTANT: This service generates OBSERVATIONS only — not diagnoses.
    The treating doctor is the sole clinical decision-maker.
    """

    SUPPORTED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

    async def analyze_image(self, image_bytes: bytes, mime_type: str) -> dict:
        """
        Analyze a medical image and return structured observations.

        Args:
            image_bytes: Raw image bytes.
            mime_type: Image MIME type.

        Returns:
            Dict with:
              - observations: str — detailed AI observations
              - key_findings: list[str]
              - disclaimer: str
              - method: str
              - success: bool
        """
        if mime_type not in self.SUPPORTED_MIME_TYPES:
            return {
                "observations": f"Unsupported image type: {mime_type}",
                "key_findings": [],
                "disclaimer": settings.AI_DISCLAIMER,
                "method": "rejected",
                "success": False,
            }

        try:
            observations, key_findings = await gemini_service.analyze_medical_image(
                image_bytes, mime_type
            )
            return {
                "observations": observations,
                "key_findings": key_findings,
                "disclaimer": settings.AI_DISCLAIMER,
                "method": "gemini-vision",
                "success": True,
            }
        except Exception as exc:
            logger.error("Vision analysis failed: %s", exc)
            return {
                "observations": (
                    "Vision analysis encountered an error. "
                    "The image has been stored and will be forwarded to the doctor."
                ),
                "key_findings": [],
                "disclaimer": settings.AI_DISCLAIMER,
                "method": "error",
                "success": False,
            }


# Singleton instance
vision_service = VisionService()
