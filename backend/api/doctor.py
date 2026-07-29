"""
ArogyaMitra AI — Doctor API Routes

POST /doctor/register       — Register a new doctor (admin)
POST /doctor/login          — Doctor login → JWT token
GET  /doctor/consultations  — List consultations assigned to this doctor
GET  /doctor/consultation/{id} — Get full consultation detail
POST /doctor/consultation   — Take action on a consultation (accept/reject/call)
POST /doctor/prescription   — Issue a prescription
GET  /doctor/patients       — List patients this doctor has consulted
"""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.doctor import Doctor
from backend.models.consultation import Consultation, ConsultationStatus, Prescription, LearningRecord
from backend.models.patient import Patient
from backend.schemas.doctor import (
    DoctorCreate,
    DoctorLogin,
    DoctorResponse,
    TokenResponse,
    ConsultationActionRequest,
    ConsultationActionResponse,
    PrescriptionCreate,
    PrescriptionResponse,
)
from backend.schemas.consultation import ConsultationDetailResponse, ConsultationSummaryResponse
from backend.utils.auth import hash_password, verify_password, create_access_token, get_current_doctor_id
from backend.services.timeline_service import timeline_service
from backend.models.timeline import TimelineEventType
from backend.agents.timeline import timeline_agent
from backend.utils.helpers import safe_json_dumps

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/doctor", tags=["Doctor"])


# ── Registration ──────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new doctor",
)
async def register_doctor(
    payload: DoctorCreate,
    db: AsyncSession = Depends(get_db),
) -> DoctorResponse:
    """Register a new doctor in the system."""
    # Check for duplicate email
    result = await db.execute(select(Doctor).where(Doctor.email.ilike(payload.email)))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A doctor with email '{payload.email}' is already registered.",
        )

    doctor_data = payload.model_dump(exclude={"password"})
    doctor_data["hashed_password"] = hash_password(payload.password)
    doctor = Doctor(**doctor_data)
    db.add(doctor)
    await db.flush()
    await db.refresh(doctor)
    logger.info("New doctor registered: id=%d email=%s", doctor.id, doctor.email)
    return doctor  # type: ignore


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Doctor login — returns JWT access token",
    description=(
        "Authenticate with email and password. Returns a Bearer JWT token "
        "required for all doctor-authenticated endpoints."
    ),
)
async def doctor_login(
    credentials: DoctorLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate a doctor and return a JWT access token."""
    result = await db.execute(
        select(Doctor).where(Doctor.email.ilike(credentials.email))
    )
    doctor = result.scalars().first()

    if not doctor or not verify_password(credentials.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This doctor account is inactive. Please contact the administrator.",
        )

    token = create_access_token(data={"sub": doctor.email, "doctor_id": doctor.id})
    logger.info("Doctor logged in: id=%d email=%s", doctor.id, doctor.email)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        doctor_id=doctor.id,
        name=doctor.name,
        specialization=doctor.specialization,
    )


# ── Consultations list ────────────────────────────────────────────────────────

@router.get(
    "/consultations",
    response_model=list[ConsultationSummaryResponse],
    summary="List consultations assigned to this doctor",
)
async def list_my_consultations(
    doctor_id: int = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db),
) -> list[ConsultationSummaryResponse]:
    """Return all consultations currently assigned to the authenticated doctor."""
    result = await db.execute(
        select(Consultation)
        .where(Consultation.doctor_id == doctor_id)
        .order_by(Consultation.created_at.desc())
    )
    consultations = result.scalars().all()
    return consultations  # type: ignore


@router.get(
    "/consultation/{consultation_id}",
    response_model=ConsultationDetailResponse,
    summary="Get full consultation detail",
    description=(
        "Retrieve the complete consultation record including: patient information, "
        "AI-generated summary, conversation history, follow-up answers, "
        "uploaded reports, and image observations."
    ),
)
async def get_consultation_detail(
    consultation_id: int,
    doctor_id: int = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db),
) -> ConsultationDetailResponse:
    """Fetch the full detail of a consultation assigned to this doctor."""
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == consultation_id,
            Consultation.doctor_id == doctor_id,
        )
    )
    consultation = result.scalars().first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation {consultation_id} not found or not assigned to you.",
        )
    return consultation  # type: ignore


# ── Consultation action ────────────────────────────────────────────────────────

@router.post(
    "/consultation",
    response_model=ConsultationActionResponse,
    summary="Take action on a consultation",
    description=(
        "Doctor can: **accept** (begin reviewing), **reject** (decline the consultation), "
        "or **call** (mark that the doctor is calling the patient). "
        "Only consultations assigned to the authenticated doctor can be acted upon."
    ),
)
async def consultation_action(
    payload: ConsultationActionRequest,
    doctor_id: int = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db),
) -> ConsultationActionResponse:
    """Accept, reject, or initiate a call for a consultation."""
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == payload.consultation_id,
            Consultation.doctor_id == doctor_id,
        )
    )
    consultation = result.scalars().first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation {payload.consultation_id} not found or not assigned to you.",
        )

    action = payload.action.lower()
    if action == "accept":
        consultation.status = ConsultationStatus.IN_PROGRESS
        if payload.notes:
            consultation.doctor_notes = payload.notes
        message = "Consultation accepted. You are now reviewing this patient."

    elif action == "reject":
        consultation.status = ConsultationStatus.REJECTED
        if payload.notes:
            consultation.doctor_notes = payload.notes
        message = "Consultation rejected."

    elif action == "call":
        # Mark status as in-progress and note the call
        consultation.status = ConsultationStatus.IN_PROGRESS
        existing_notes = consultation.doctor_notes or ""
        consultation.doctor_notes = f"{existing_notes}\n[Doctor initiated call]".strip()
        message = "Call initiated. Patient will be notified."

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown action '{action}'. Must be one of: accept, reject, call.",
        )

    await db.flush()

    # Timeline event
    await timeline_service.add_event(
        db=db,
        patient_id=consultation.patient_id,
        event_type=TimelineEventType.DOCTOR_NOTE,
        title=f"Doctor Action: {action.title()}",
        description=payload.notes or message,
        consultation_id=consultation.id,
    )

    return ConsultationActionResponse(
        consultation_id=consultation.id,
        status=consultation.status.value,
        message=message,
    )


# ── Prescription ──────────────────────────────────────────────────────────────

@router.post(
    "/prescription",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Issue a prescription for a consultation",
    description=(
        "Doctor issues a prescription after reviewing the AI-assisted consultation. "
        "Includes diagnosis, medicines, instructions, and optional hospital referral. "
        "This action marks the consultation as **completed** and records it in the health timeline."
    ),
)
async def issue_prescription(
    payload: PrescriptionCreate,
    doctor_id: int = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db),
) -> PrescriptionResponse:
    """Issue a prescription and close the consultation."""
    # Load consultation
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == payload.consultation_id,
            Consultation.doctor_id == doctor_id,
        )
    )
    consultation = result.scalars().first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation {payload.consultation_id} not found or not assigned to you.",
        )

    if consultation.status == ConsultationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A prescription has already been issued for this consultation.",
        )

    # Load doctor for timeline
    doctor_result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = doctor_result.scalars().first()

    # Build medicines JSON
    medicines_json = safe_json_dumps([m.model_dump() for m in payload.medicines])

    # Create prescription
    prescription = Prescription(
        consultation_id=payload.consultation_id,
        doctor_id=doctor_id,
        patient_id=consultation.patient_id,
        medicines=medicines_json,
        diagnosis=payload.diagnosis,
        instructions=payload.instructions,
        follow_up_date=payload.follow_up_date,
    )
    db.add(prescription)

    # Update consultation
    consultation.status = ConsultationStatus.COMPLETED
    consultation.doctor_notes = payload.doctor_notes or consultation.doctor_notes
    if payload.referral_hospital:
        consultation.referral_hospital = payload.referral_hospital
        consultation.status = ConsultationStatus.REFERRED

    await db.flush()

    # Create learning record (anonymized)
    learning_record = LearningRecord(
        consultation_id=payload.consultation_id,
        ai_summary=consultation.ai_summary,
        doctor_summary=payload.diagnosis,
        prescription_data=medicines_json,
        symptom_keywords=consultation.chief_complaint,
    )
    db.add(learning_record)
    await db.flush()

    # Timeline events
    await timeline_agent.record_prescription(
        db=db,
        patient_id=consultation.patient_id,
        consultation_id=consultation.id,
        doctor_name=doctor.name if doctor else "Doctor",
        diagnosis=payload.diagnosis,
    )

    if payload.referral_hospital:
        await timeline_agent.record_referral(
            db=db,
            patient_id=consultation.patient_id,
            consultation_id=consultation.id,
            hospital=payload.referral_hospital,
            doctor_name=doctor.name if doctor else "Doctor",
        )

    await db.refresh(prescription)
    logger.info(
        "Prescription issued: id=%d consultation=%d doctor=%d",
        prescription.id,
        consultation.id,
        doctor_id,
    )
    return prescription  # type: ignore


# ── Doctor profile ─────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=DoctorResponse,
    summary="Get authenticated doctor's profile",
)
async def get_my_profile(
    doctor_id: int = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db),
) -> DoctorResponse:
    """Return the authenticated doctor's profile."""
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalars().first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found.",
        )
    return doctor  # type: ignore
