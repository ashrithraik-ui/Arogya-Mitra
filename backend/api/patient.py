"""
ArogyaMitra AI — Patient API Routes

POST /patient/register   — Register a new patient
POST /patient/chat       — Send a text message to the AI assistant
POST /patient/voice      — Send a voice recording to the AI assistant
POST /patient/report     — Upload a medical report (PDF/image) for OCR + AI explanation
POST /patient/image      — Upload a medical image for AI vision analysis
GET  /patient/timeline   — Get the patient's health timeline
GET  /patient/{id}       — Get patient profile
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.patient import Patient
from backend.schemas.patient import (
    PatientCreate,
    PatientResponse,
    ChatRequest,
    ChatResponse,
    VoiceResponse,
    ReportAnalysisResponse,
    ImageAnalysisResponse,
)
from backend.schemas.timeline import PatientTimelineResponse
from backend.agents.orchestrator import orchestrator_agent
from backend.agents.voice import voice_agent
from backend.agents.ocr_agent import ocr_agent
from backend.agents.vision import vision_agent
from backend.agents.conversation import conversation_agent
from backend.services.timeline_service import timeline_service
from backend.storage.file_storage import file_storage
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/patient", tags=["Patient"])


# ── Register ──────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient",
)
async def register_patient(
    payload: PatientCreate,
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """
    Register a new patient. Phone number is the unique identifier.
    Returns the created patient record.
    """
    # Check for duplicate phone
    result = await db.execute(select(Patient).where(Patient.phone == payload.phone))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A patient with phone '{payload.phone}' is already registered.",
        )

    patient = Patient(**payload.model_dump())
    db.add(patient)
    await db.flush()
    await db.refresh(patient)
    logger.info("New patient registered: id=%d phone=%s", patient.id, patient.phone)
    return patient  # type: ignore


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient profile",
)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """Retrieve a patient's profile by ID."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id={patient_id} not found.",
        )
    return patient  # type: ignore


# ── Chat ──────────────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a text message to the AI assistant",
    description=(
        "Patient sends a text message. The AI collects symptoms and follow-up information "
        "through a dynamic conversation. When enough information is gathered, an AI summary "
        "is generated and forwarded to an available doctor for review. "
        "**The AI does NOT diagnose or prescribe.**"
    ),
)
async def patient_chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Process one patient chat turn through the full agent pipeline:
    ConversationAgent → FollowUpAgent → MedicalHistoryAgent → SummaryAgent → DoctorRoutingAgent.
    """
    # Verify patient exists
    result = await db.execute(select(Patient).where(Patient.id == payload.patient_id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id={payload.patient_id} not found.",
        )

    try:
        response = await orchestrator_agent.handle_chat(
            db=db,
            patient_id=payload.patient_id,
            consultation_id=payload.consultation_id,
            message=payload.message,
        )
        return ChatResponse(**response)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.error("Chat processing error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message. Please try again.",
        )


# ── Voice ─────────────────────────────────────────────────────────────────────

@router.post(
    "/voice",
    response_model=VoiceResponse,
    summary="Send a voice recording to the AI assistant",
    description=(
        "Upload an audio file (WAV, MP3, OGG). The AI transcribes it, generates a response, "
        "and optionally returns a synthesized audio reply. "
        "**Future: faster-whisper integration for production-grade multilingual transcription.**"
    ),
)
async def patient_voice(
    patient_id: int = Form(..., description="Patient ID"),
    consultation_id: int | None = Form(None, description="Existing consultation ID (optional)"),
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, OGG, FLAC, M4A)"),
    db: AsyncSession = Depends(get_db),
) -> VoiceResponse:
    """Process a voice audio file through the VoiceAgent pipeline."""
    # Verify patient exists
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id={patient_id} not found.",
        )

    # Read audio bytes
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty.",
        )

    # Save audio file
    saved = await file_storage.save_file(
        audio,
        file_type="voice",
        allowed_types=None,  # Accept all audio types
    )

    # Get or create consultation
    consultation = await conversation_agent.get_or_create_consultation(
        db=db,
        patient_id=patient_id,
        consultation_id=consultation_id,
        chief_complaint="[Voice consultation]",
    )

    # Process through VoiceAgent
    result_data = await voice_agent.process_voice(
        db=db,
        consultation=consultation,
        audio_bytes=audio_bytes,
        content_type=audio.content_type or "audio/wav",
    )

    return VoiceResponse(
        consultation_id=consultation.id,
        transcribed_text=result_data["transcribed_text"],
        ai_response=result_data["ai_response"],
        follow_up_question=result_data.get("follow_up_question"),
        audio_response_path=saved["file_path"] if result_data.get("audio_response_base64") else None,
        disclaimer=result_data["disclaimer"],
    )


# ── Report OCR ────────────────────────────────────────────────────────────────

@router.post(
    "/report",
    response_model=ReportAnalysisResponse,
    summary="Upload a medical report for OCR and AI explanation",
    description=(
        "Upload a PDF or image of a medical report. The system extracts the text via OCR "
        "and provides a plain-language explanation. **The AI does NOT interpret results clinically.** "
        "The report is forwarded to the doctor for clinical review."
    ),
)
async def upload_report(
    patient_id: int = Form(..., description="Patient ID"),
    consultation_id: int | None = Form(None, description="Existing consultation ID (optional)"),
    report: UploadFile = File(..., description="PDF or image of a medical report"),
    db: AsyncSession = Depends(get_db),
) -> ReportAnalysisResponse:
    """Process an uploaded medical report through OCR + AI explanation."""
    # Verify patient exists
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id={patient_id} not found.",
        )

    # Save file
    saved = await file_storage.save_file(
        report,
        file_type="report",
        allowed_types=settings.ALLOWED_DOC_TYPES + ["application/pdf"],
    )

    # Get or create consultation
    consultation = await conversation_agent.get_or_create_consultation(
        db=db,
        patient_id=patient_id,
        consultation_id=consultation_id,
        chief_complaint="[Medical report uploaded]",
    )
    await conversation_agent.add_uploaded_file(db, consultation, saved["file_path"])

    # Read the saved file bytes for OCR
    file_bytes = await file_storage.read_file_bytes(saved["file_path"])

    # Process through OCRAgent
    ocr_result = await ocr_agent.process_report(
        db=db,
        consultation=consultation,
        file_bytes=file_bytes,
        content_type=report.content_type or "application/pdf",
        file_path=saved["file_path"],
    )

    return ReportAnalysisResponse(
        consultation_id=consultation.id,
        extracted_text=ocr_result["extracted_text"],
        simplified_explanation=ocr_result["explanation"],
        key_findings=ocr_result["key_findings"],
        disclaimer=ocr_result["disclaimer"],
    )


# ── Medical Image Vision ──────────────────────────────────────────────────────

@router.post(
    "/image",
    response_model=ImageAnalysisResponse,
    summary="Upload a medical image for AI vision analysis",
    description=(
        "Upload a medical image (X-ray, MRI, skin photo, etc.). The AI generates preliminary "
        "observations and forwards them to the doctor. "
        "**The AI does NOT diagnose. All clinical decisions are made by the doctor.**"
    ),
)
async def upload_image(
    patient_id: int = Form(..., description="Patient ID"),
    consultation_id: int | None = Form(None, description="Existing consultation ID (optional)"),
    image: UploadFile = File(..., description="Medical image (JPEG, PNG, WEBP)"),
    db: AsyncSession = Depends(get_db),
) -> ImageAnalysisResponse:
    """Analyze a medical image through the VisionAgent pipeline."""
    # Verify patient exists
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id={patient_id} not found.",
        )

    # Save image
    saved = await file_storage.save_file(
        image,
        file_type="image",
        allowed_types=settings.ALLOWED_IMAGE_TYPES,
    )

    # Get or create consultation
    consultation = await conversation_agent.get_or_create_consultation(
        db=db,
        patient_id=patient_id,
        consultation_id=consultation_id,
        chief_complaint="[Medical image uploaded]",
    )
    await conversation_agent.add_uploaded_file(db, consultation, saved["file_path"])

    # Read image bytes for vision analysis
    image_bytes = await file_storage.read_file_bytes(saved["file_path"])

    # Process through VisionAgent
    vision_result = await vision_agent.process_image(
        db=db,
        consultation=consultation,
        image_bytes=image_bytes,
        mime_type=image.content_type or "image/jpeg",
        file_path=saved["file_path"],
    )

    # Route to doctor if not already assigned
    if not consultation.doctor_id:
        await doctor_routing_agent.route_consultation(db, consultation)

    return ImageAnalysisResponse(
        consultation_id=consultation.id,
        observations=vision_result["observations"],
        key_findings=vision_result["key_findings"],
        forwarded_to_doctor=vision_result["forwarded_to_doctor"],
        disclaimer=vision_result["disclaimer"],
    )


# ── Timeline ──────────────────────────────────────────────────────────────────

@router.get(
    "/timeline",
    response_model=PatientTimelineResponse,
    summary="Get the patient's health timeline",
    description=(
        "Returns a chronological list of health events for the patient: "
        "consultations, reports, images, prescriptions, and doctor notes."
    ),
)
async def get_patient_timeline(
    patient_id: int = Query(..., description="Patient ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum events to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
) -> PatientTimelineResponse:
    """Retrieve paginated health timeline events for a patient."""
    # Verify patient exists
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id={patient_id} not found.",
        )

    events = await timeline_service.get_patient_timeline(
        db=db,
        patient_id=patient_id,
        limit=limit,
        offset=offset,
    )
    total = await timeline_service.get_event_count(db=db, patient_id=patient_id)

    return PatientTimelineResponse(
        patient_id=patient_id,
        total_events=total,
        events=events,  # type: ignore
    )
