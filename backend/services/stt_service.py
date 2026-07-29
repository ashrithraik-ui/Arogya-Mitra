"""
ArogyaMitra AI — Speech-to-Text Service
Converts patient audio recordings to text.

Current: Uses openai-whisper (if installed) or SpeechRecognition.
Future Integration: faster-whisper for GPU-accelerated, multilingual transcription.
"""

import io
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """
    Transcribes patient voice recordings.

    Supported formats: WAV, MP3, OGG, FLAC, M4A.
    Future: faster-whisper integration for production-grade transcription.
    """

    async def transcribe(self, audio_bytes: bytes, content_type: str = "audio/wav") -> dict:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Raw audio file bytes.
            content_type: MIME type of the audio.

        Returns:
            Dict with keys:
              - text: Transcribed text string.
              - language: Detected language (if available).
              - confidence: Float 0-1 (if available).
              - method: Transcription method used.
              - success: bool
        """
        # Try openai-whisper first
        result = await self._transcribe_with_whisper(audio_bytes, content_type)
        if result["success"]:
            return result

        # Fallback: SpeechRecognition
        result = await self._transcribe_with_sr(audio_bytes)
        if result["success"]:
            return result

        # Final fallback
        return {
            "text": (
                "[Voice transcription not available. "
                "Please type your symptoms instead. "
                "Future: faster-whisper integration will enable voice input.]"
            ),
            "language": "unknown",
            "confidence": 0.0,
            "method": "fallback",
            "success": False,
        }

    async def _transcribe_with_whisper(
        self, audio_bytes: bytes, content_type: str
    ) -> dict:
        """Transcribe using openai-whisper."""
        try:
            import whisper  # type: ignore

            # Determine extension from content type
            ext_map = {
                "audio/wav": ".wav",
                "audio/mp3": ".mp3",
                "audio/mpeg": ".mp3",
                "audio/ogg": ".ogg",
                "audio/flac": ".flac",
                "audio/m4a": ".m4a",
                "audio/mp4": ".mp4",
            }
            ext = ext_map.get(content_type, ".wav")

            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            model = whisper.load_model("base")
            result = model.transcribe(tmp_path)
            Path(tmp_path).unlink(missing_ok=True)

            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", "unknown"),
                "confidence": 1.0,
                "method": "openai-whisper",
                "success": True,
            }
        except ImportError:
            return {"text": "", "method": "whisper_unavailable", "success": False}
        except Exception as exc:
            logger.error("Whisper transcription failed: %s", exc)
            return {"text": "", "method": "whisper_error", "success": False}

    async def _transcribe_with_sr(self, audio_bytes: bytes) -> dict:
        """Transcribe using SpeechRecognition library (Google Web Speech API)."""
        try:
            import speech_recognition as sr  # type: ignore

            recognizer = sr.Recognizer()
            audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
            with audio_file as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return {
                "text": text.strip(),
                "language": "en",
                "confidence": 0.9,
                "method": "speech-recognition",
                "success": True,
            }
        except ImportError:
            return {"text": "", "method": "sr_unavailable", "success": False}
        except Exception as exc:
            logger.error("SpeechRecognition failed: %s", exc)
            return {"text": "", "method": "sr_error", "success": False}


class TextToSpeechService:
    """
    Converts AI text responses to speech audio.

    Future Integration: edge-tts for natural-sounding multilingual TTS.
    """

    async def synthesize(self, text: str, language: str = "en") -> dict:
        """
        Convert text to speech audio bytes.

        Args:
            text: Input text to synthesize.
            language: Language code (e.g. 'en', 'hi').

        Returns:
            Dict with keys:
              - audio_bytes: bytes or None
              - content_type: str
              - method: str
              - success: bool
        """
        result = await self._synthesize_with_edge_tts(text, language)
        if result["success"]:
            return result

        return {
            "audio_bytes": None,
            "content_type": "audio/mp3",
            "method": "fallback",
            "success": False,
            "message": (
                "Text-to-speech not available. "
                "Future: edge-tts integration will provide voice responses."
            ),
        }

    async def _synthesize_with_edge_tts(self, text: str, language: str) -> dict:
        """Synthesize using edge-tts (Microsoft Edge TTS)."""
        try:
            import edge_tts  # type: ignore

            voice_map = {
                "en": "en-IN-NeerjaNeural",
                "hi": "hi-IN-SwaraNeural",
                "ta": "ta-IN-PallaviNeural",
                "te": "te-IN-ShrutiNeural",
                "bn": "bn-IN-TanishaaNeural",
            }
            voice = voice_map.get(language, "en-IN-NeerjaNeural")

            communicate = edge_tts.Communicate(text, voice)
            audio_parts: list[bytes] = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_parts.append(chunk["data"])

            audio_bytes = b"".join(audio_parts)
            return {
                "audio_bytes": audio_bytes,
                "content_type": "audio/mpeg",
                "method": "edge-tts",
                "success": True,
            }
        except ImportError:
            return {"audio_bytes": None, "success": False}
        except Exception as exc:
            logger.error("edge-tts failed: %s", exc)
            return {"audio_bytes": None, "success": False}


# Singleton instances
stt_service = SpeechToTextService()
tts_service = TextToSpeechService()
