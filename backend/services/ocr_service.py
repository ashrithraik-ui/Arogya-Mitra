"""
ArogyaMitra AI — OCR Service
Extracts text from PDFs and images using PIL and pytesseract (if available).
Falls back to pillow-based basic extraction with a clear status message.

Future integration: EasyOCR for enhanced multilingual OCR.
"""

import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional imports — graceful degradation if not installed
try:
    from PIL import Image  # type: ignore
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not installed. Image OCR will be limited.")


class OCRService:
    """
    Extracts text content from uploaded documents and images.

    Current capabilities:
      - PDF text extraction (via pdfplumber if installed)
      - Basic image-to-text (via pytesseract if installed)
      - Pillow image loading and metadata extraction (always available)

    Future: Replace with EasyOCR for multilingual, GPU-accelerated OCR.
    """

    async def extract_text_from_file(
        self, file_bytes: bytes, content_type: str
    ) -> dict:
        """
        Extract text from a file based on its MIME type.

        Args:
            file_bytes: Raw file bytes.
            content_type: MIME type (e.g. 'application/pdf', 'image/jpeg').

        Returns:
            Dict with keys:
              - extracted_text: str
              - page_count: int (for PDFs)
              - method: str (extraction method used)
              - success: bool
        """
        if content_type == "application/pdf":
            return await self._extract_from_pdf(file_bytes)
        elif content_type.startswith("image/"):
            return await self._extract_from_image(file_bytes)
        else:
            return {
                "extracted_text": "",
                "page_count": 0,
                "method": "unsupported",
                "success": False,
                "message": f"Unsupported file type for OCR: {content_type}",
            }

    async def _extract_from_pdf(self, file_bytes: bytes) -> dict:
        """Extract text from a PDF using pdfplumber (if installed)."""
        try:
            import pdfplumber  # type: ignore

            text_parts = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

            extracted = "\n\n".join(text_parts).strip()
            return {
                "extracted_text": extracted or "[PDF contains no extractable text — may be scanned.]",
                "page_count": page_count,
                "method": "pdfplumber",
                "success": bool(extracted),
            }
        except ImportError:
            # pdfplumber not installed — return placeholder
            return {
                "extracted_text": (
                    "[PDF text extraction requires pdfplumber. "
                    "Run: pip install pdfplumber\n\n"
                    "Future: EasyOCR integration will handle scanned PDFs.]"
                ),
                "page_count": 0,
                "method": "fallback",
                "success": False,
            }
        except Exception as exc:
            logger.error("PDF extraction failed: %s", exc)
            return {
                "extracted_text": f"[PDF extraction error: {exc}]",
                "page_count": 0,
                "method": "error",
                "success": False,
            }

    async def _extract_from_image(self, file_bytes: bytes) -> dict:
        """Extract text from an image using pytesseract (if installed)."""
        if not PIL_AVAILABLE:
            return {
                "extracted_text": "[Image OCR unavailable: Pillow not installed.]",
                "page_count": 1,
                "method": "unavailable",
                "success": False,
            }

        try:
            import pytesseract  # type: ignore
            from PIL import Image

            image = Image.open(io.BytesIO(file_bytes))
            extracted = pytesseract.image_to_string(image).strip()
            return {
                "extracted_text": extracted or "[No readable text found in image.]",
                "page_count": 1,
                "method": "pytesseract",
                "success": bool(extracted),
            }
        except ImportError:
            # pytesseract not installed — return image metadata only
            try:
                from PIL import Image
                image = Image.open(io.BytesIO(file_bytes))
                return {
                    "extracted_text": (
                        f"[Image loaded: {image.format} {image.size[0]}×{image.size[1]}px. "
                        "Text extraction requires pytesseract. "
                        "Future: EasyOCR will provide multilingual text extraction.]"
                    ),
                    "page_count": 1,
                    "method": "pillow_metadata",
                    "success": False,
                }
            except Exception:
                return {
                    "extracted_text": "[Image OCR not available. Image stored for doctor review.]",
                    "page_count": 1,
                    "method": "fallback",
                    "success": False,
                }
        except Exception as exc:
            logger.error("Image OCR failed: %s", exc)
            return {
                "extracted_text": f"[OCR error: {exc}]",
                "page_count": 1,
                "method": "error",
                "success": False,
            }


# Singleton instance
ocr_service = OCRService()
