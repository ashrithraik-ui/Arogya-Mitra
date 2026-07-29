"""
ArogyaMitra AI — JSON-backed API Routes
Simple routes that use JSON file storage for all data persistence.
Mounted at /api/ and provides the complete patient-doctor-prescription flow.
"""

import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from backend.storage.json_store import (
    get_all_patients, get_patient, get_patient_by_phone, save_patient,
    get_all_doctors, get_doctor, get_doctor_by_email, save_doctor,
    get_all_consultations, get_consultation, get_consultations_by_patient,
    get_consultations_by_doctor, get_active_consultation, save_consultation,
    get_all_prescriptions, get_prescriptions_by_patient,
    get_prescriptions_by_consultation, save_prescription,
    get_timeline, add_timeline_event, seed_defaults,
)
from backend.services.gemini_service import gemini_service
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["JSON API"])


# ── Request/Response Models ───────────────────────────────────────────────────

class PatientRegisterReq(BaseModel):
    name: str
    phone: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    known_conditions: Optional[str] = None
    current_medications: Optional[str] = None

class ChatReq(BaseModel):
    patient_id: int
    message: str
    consultation_id: Optional[int] = None

class DoctorLoginReq(BaseModel):
    email: str
    password: str

class DoctorNotesReq(BaseModel):
    consultation_id: int
    notes: str

class PrescriptionReq(BaseModel):
    consultation_id: int
    doctor_id: int
    diagnosis: str
    medicines: list[dict]  # [{name, dose, frequency, duration}]
    instructions: Optional[str] = ""
    follow_up_date: Optional[str] = None

class NewChatReq(BaseModel):
    patient_id: int
    chief_complaint: Optional[str] = "Follow-up Consultation"

class ConsultationActionReq(BaseModel):
    consultation_id: int
    action: str  # accept, reject, call
    notes: Optional[str] = ""
    doctor_id: Optional[int] = None


# ── Patient Routes ────────────────────────────────────────────────────────────

@router.post("/patient/register")
async def register_patient(payload: PatientRegisterReq):
    existing = get_patient_by_phone(payload.phone)
    if existing:
        return existing
    patient = save_patient(payload.model_dump())
    logger.info("Patient registered: %s (id=%d)", patient["name"], patient["id"])
    return patient


@router.post("/patient/chat")
async def patient_chat(payload: ChatReq):
    patient = get_patient(payload.patient_id)
    if not patient:
        # Auto-create patient if not found (for smooth demo experience)
        patient = save_patient({
            "id": payload.patient_id,
            "name": "Ravi Kumar",
            "phone": "+910000000001",
            "age": 35,
            "gender": "Male",
            "blood_group": "O+"
        })

    # Get or create consultation
    consultation = None
    if payload.consultation_id:
        consultation = get_consultation(payload.consultation_id)

    if not consultation:
        consultation = get_active_consultation(payload.patient_id)

    if not consultation:
        doctors = get_all_doctors()
        assigned_doc = doctors[0]["id"] if doctors else None

        consultation = save_consultation({
            "patient_id": payload.patient_id,
            "status": "assigned" if assigned_doc else "pending",
            "chief_complaint": payload.message,
            "conversation_history": [],
            "follow_up_answers": {},
            "ai_summary": f"Patient symptoms reported: {payload.message}",
            "vision_observations": None,
            "uploaded_files": [],
            "doctor_id": assigned_doc,
            "doctor_notes": None,
        })
        add_timeline_event({
            "patient_id": payload.patient_id,
            "event_type": "CONSULTATION",
            "title": "Consultation Started & Forwarded to Doctor",
            "description": f"Patient described: {payload.message[:100]}",
            "consultation_id": consultation["id"],
        })

    # Add patient message to history
    history = consultation.get("conversation_history", [])
    history.append({
        "role": "patient",
        "message": payload.message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # Get AI response via Gemini or fallback
    try:
        ai_ack = await gemini_service.generate_ai_chat_response(
            user_message=payload.message,
            chief_complaint=consultation.get("chief_complaint", payload.message),
            follow_up_answers=consultation.get("follow_up_answers", {}),
            conversation_history=history[-6:],
        )
    except Exception as e:
        logger.error("Gemini service error: %s", e)
        ai_ack = "Thank you for sharing your symptoms."

    if not ai_ack:
        ai_ack = "Thank you for sharing your symptoms."

    # Get follow-up question
    try:
        follow_up = await gemini_service.get_follow_up_question(
            chief_complaint=consultation.get("chief_complaint", payload.message),
            collected_info=consultation.get("follow_up_answers", {}),
            conversation_history=history[-6:],
        )
    except Exception:
        follow_up = None

    # Ensure doctor assignment so doctor receives patient data immediately
    if not consultation.get("doctor_id"):
        doctors = get_all_doctors()
        if doctors:
            consultation["doctor_id"] = doctors[0]["id"]
            consultation["status"] = "assigned"

    is_summary_ready = "SUMMARY_READY" in (follow_up or "").upper() if follow_up else False

    if is_summary_ready:
        final_response = (
            f"{ai_ack}\n\n"
            "I have collected all necessary information. "
            "Your health summary has been prepared and forwarded to your doctor for clinical review."
        )
    else:
        if follow_up and follow_up.strip() and "SUMMARY_READY" not in follow_up:
            final_response = f"{ai_ack}\n\n{follow_up.strip()}"
        else:
            final_response = f"{ai_ack}\n\nYour message has been updated and sent to your assigned doctor."

    # Add AI response to history
    history.append({
        "role": "ai",
        "message": final_response,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    consultation["conversation_history"] = history
    
    # Update AI Summary for doctor review
    summary_text = f"Chief Complaint: {consultation.get('chief_complaint', '')}\n\nConversation Details:\n"
    for m in history:
        role_label = m.get('role', 'patient').upper()
        if role_label == 'DOCTOR':
            role_label = f"DOCTOR ({m.get('doctor_name', 'Doctor')})"
        summary_text += f"- {role_label}: {m.get('message', '')}\n"
    consultation["ai_summary"] = summary_text

    # Re-open consultation for doctor attention if patient sends follow-up
    if consultation.get("status") in ["completed", "assigned"]:
        consultation["status"] = "in_progress"

    # Save consultation
    save_consultation(consultation)

    return {
        "consultation_id": consultation["id"],
        "ai_response": final_response,
        "is_summary_ready": is_summary_ready,
        "status": consultation["status"],
    }


class CallChatReq(BaseModel):
    caller_number: Optional[str] = "Unknown"
    message: str
    consultation_id: Optional[int] = None

@router.post("/call/chat")
async def call_chat(payload: CallChatReq):
    """
    Dedicated endpoint for the Android AI Call Assistant app.
    Takes caller phone number and spoken text message, manages/creates patient consultation,
    and returns text response for TTS output on phone call.
    """
    phone = payload.caller_number or "+910000000001"
    patient = get_patient_by_phone(phone)
    if not patient:
        patient = save_patient({
            "name": f"Caller ({phone[-4:] if len(phone)>=4 else 'Unknown'})",
            "phone": phone,
            "age": 30,
            "gender": "Unknown"
        })

    patient_id = patient["id"]
    chat_payload = ChatReq(
        patient_id=patient_id,
        message=payload.message,
        consultation_id=payload.consultation_id
    )
    return await patient_chat(chat_payload)


@router.post("/call/voice")
async def call_voice(
    audio_file: UploadFile = File(...),
    caller_number: str = Form(default="Unknown"),
    consultation_id: Optional[int] = Form(default=None),
):
    """
    Receive WAV audio from the Android phone call, transcribe with Gemini,
    generate AI response, and return both transcribed text + AI response.
    The Android app records audio via speakerphone acoustic loopback.
    """
    import base64
    import tempfile
    import os

    logger.info("🎤 /call/voice — Received audio from %s (consultation_id=%s)", caller_number, consultation_id)

    # Read uploaded WAV
    audio_bytes = await audio_file.read()
    logger.info("Audio file size: %d bytes", len(audio_bytes))

    # ── Step 1: Transcribe audio with Gemini ──────────────────────────────
    transcribed_text = ""
    try:
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        from google import genai
        from google.genai import types as genai_types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        audio_part = genai_types.Part.from_bytes(
            data=audio_bytes,
            mime_type="audio/wav"
        )

        transcribe_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                audio_part,
                "Transcribe this audio exactly. If you hear speech, return ONLY the exact words spoken. "
                "If the audio is silent or has no speech, respond with exactly: [SILENCE]. "
                "Do NOT add any commentary or explanation."
            ]
        )
        transcribed_text = transcribe_response.text.strip() if transcribe_response.text else ""
        logger.info("📝 Gemini Transcription: '%s'", transcribed_text)
    except Exception as e:
        logger.error("Gemini transcription error: %s", e)
        transcribed_text = ""

    # Handle silence / no speech detected
    if not transcribed_text or "[SILENCE]" in transcribed_text.upper() or len(transcribed_text) < 3:
        return {
            "consultation_id": consultation_id,
            "transcribed_text": "",
            "ai_response": "I could not hear you clearly. Please speak louder into your phone and describe your symptoms.",
            "status": "no_speech"
        }

    # ── Step 2: Get or create patient & consultation ──────────────────────
    phone = caller_number or "+910000000001"
    patient = get_patient_by_phone(phone)
    if not patient:
        patient = save_patient({
            "name": f"Caller ({phone[-4:] if len(phone)>=4 else 'Unknown'})",
            "phone": phone,
            "age": 30,
            "gender": "Unknown"
        })

    patient_id = patient["id"]

    # ── Step 3: Send transcribed text through normal chat pipeline ────────
    chat_payload = ChatReq(
        patient_id=patient_id,
        message=transcribed_text,
        consultation_id=consultation_id,
    )
    chat_result = await patient_chat(chat_payload)

    return {
        "consultation_id": chat_result.get("consultation_id"),
        "transcribed_text": transcribed_text,
        "ai_response": chat_result.get("ai_response", "Thank you. Your details have been forwarded to the doctor."),
        "status": "ok"
    }


@router.post("/patient/new-chat")
async def create_new_patient_chat(payload: NewChatReq):
    """Start a brand new consultation / follow-up chat for a patient."""
    patient = get_patient(payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctors = get_all_doctors()
    assigned_doc = doctors[0]["id"] if doctors else None

    initial_msg = f"Hello! I am ArogyaMitra AI. This is a new follow-up chat session regarding: '{payload.chief_complaint}'. Please describe your symptoms or updates, and I will share them with your doctor."

    consultation = save_consultation({
        "patient_id": payload.patient_id,
        "status": "assigned" if assigned_doc else "pending",
        "chief_complaint": payload.chief_complaint,
        "conversation_history": [
            {
                "role": "ai",
                "message": initial_msg,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "follow_up_answers": {},
        "ai_summary": f"Follow-up consultation created: {payload.chief_complaint}",
        "vision_observations": None,
        "uploaded_files": [],
        "doctor_id": assigned_doc,
        "doctor_notes": None,
    })

    add_timeline_event({
        "patient_id": payload.patient_id,
        "event_type": "CONSULTATION",
        "title": "New Follow-Up Chat Started",
        "description": payload.chief_complaint,
        "consultation_id": consultation["id"],
    })

    doctor = get_doctor(assigned_doc) if assigned_doc else None

    return {
        "consultation_id": consultation["id"],
        "history": consultation["conversation_history"],
        "status": consultation["status"],
        "doctor_assigned": doctor["name"] if doctor else None,
    }


@router.get("/patient/active-chat")
async def get_patient_active_chat(patient_id: int, consultation_id: Optional[int] = None):
    """Retrieve active consultation chat history for a patient, or a specific consultation if requested."""
    all_cons = get_consultations_by_patient(patient_id)
    
    consultation = None
    if consultation_id:
        consultation = get_consultation(consultation_id)

    if not consultation:
        consultation = get_active_consultation(patient_id)

    if not consultation and all_cons:
        consultation = max(all_cons, key=lambda x: x.get("id", 0))

    if not consultation:
        return {
            "consultation_id": None, 
            "history": [], 
            "status": None,
            "doctor_assigned": None, 
            "doctor_notes": None,
            "prescriptions": [],
            "all_consultations": []
        }

    doctor = get_doctor(consultation.get("doctor_id", 0)) if consultation.get("doctor_id") else None
    prescriptions = get_prescriptions_by_consultation(consultation["id"])

    # Prepare summary list of all consultations for chat session switcher
    summary_cons = []
    for c in sorted(all_cons, key=lambda x: x.get("id", 0), reverse=True):
        doc = get_doctor(c.get("doctor_id", 0)) if c.get("doctor_id") else None
        summary_cons.append({
            "id": c["id"],
            "chief_complaint": c.get("chief_complaint", "General Consultation"),
            "status": c.get("status", "pending"),
            "created_at": c.get("created_at"),
            "doctor_name": doc["name"] if doc else None,
        })

    return {
        "consultation_id": consultation["id"],
        "history": consultation.get("conversation_history", []),
        "status": consultation.get("status"),
        "doctor_assigned": doctor["name"] if doctor else None,
        "doctor_phone": doctor.get("phone", "+919876543210") if doctor else None,
        "doctor_notes": consultation.get("doctor_notes"),
        "prescriptions": prescriptions,
        "uploaded_files": consultation.get("uploaded_files", []),
        "vision_observations": consultation.get("vision_observations"),
        "all_consultations": summary_cons,
    }


@router.get("/patient/timeline")
async def patient_timeline(patient_id: int):
    events = get_timeline(patient_id)
    return {"patient_id": patient_id, "events": events, "total": len(events)}


@router.get("/patient/prescriptions")
async def patient_prescriptions(patient_id: int):
    """Get all prescriptions for a patient (sent by doctors)."""
    prescriptions = get_prescriptions_by_patient(patient_id)
    # Enrich with doctor name and phone
    for rx in prescriptions:
        doc = get_doctor(rx.get("doctor_id", 0))
        rx["doctor_name"] = doc["name"] if doc else "Doctor"
        rx["doctor_phone"] = doc.get("phone", "+919876543210") if doc else "+919876543210"
    return prescriptions


@router.get("/patient/consultations")
async def patient_consultations(patient_id: int):
    """Get all consultations for a patient, including doctor notes."""
    consultations = get_consultations_by_patient(patient_id)
    for c in consultations:
        doc = get_doctor(c.get("doctor_id", 0)) if c.get("doctor_id") else None
        c["doctor_name"] = doc["name"] if doc else None
        c["doctor_phone"] = doc.get("phone", "+919876543210") if doc else None
        # Include prescriptions
        c["prescriptions"] = get_prescriptions_by_consultation(c["id"])
    return consultations



# NOTE: This route MUST come after all other /patient/* GET routes
# otherwise FastAPI will match /patient/active-chat as /patient/{patient_id}
@router.get("/patient/{patient_id}")
async def patient_profile(patient_id: int):
    p = get_patient(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p


# ── Doctor Routes ─────────────────────────────────────────────────────────────

@router.post("/doctor/login")
async def doctor_login(payload: DoctorLoginReq):
    doctor = get_doctor_by_email(payload.email)
    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if doctor.get("password") != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    from backend.utils.auth import create_access_token
    token = create_access_token({"sub": doctor["email"], "doctor_id": doctor["id"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "doctor_id": doctor["id"],
        "name": doctor["name"],
        "specialization": doctor.get("specialization", "General Physician"),
    }


@router.get("/doctor/me")
async def doctor_me():
    # For simplicity, return the first doctor (or use token later)
    doctors = get_all_doctors()
    if doctors:
        return doctors[0]
    raise HTTPException(status_code=404, detail="No doctor found")


@router.get("/doctor/consultations")
async def doctor_consultations(doctor_id: Optional[int] = None):
    """List all consultations (or filter by doctor_id)."""
    if doctor_id:
        consultations = get_consultations_by_doctor(doctor_id)
    else:
        consultations = get_all_consultations()

    # Enrich with patient info
    for c in consultations:
        patient = get_patient(c.get("patient_id", 0))
        c["patient_name"] = patient["name"] if patient else "Unknown"
        c["patient_phone"] = patient.get("phone") if patient else ""
    return consultations


@router.get("/doctor/consultation/{consultation_id}")
async def doctor_consultation_detail(consultation_id: int):
    consultation = get_consultation(consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    # Enrich
    patient = get_patient(consultation.get("patient_id", 0))
    consultation["patient"] = patient
    consultation["prescriptions"] = get_prescriptions_by_consultation(consultation_id)
    return consultation


@router.post("/doctor/consultation")
async def doctor_consultation_action(payload: ConsultationActionReq):
    consultation = get_consultation(payload.consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    doctor = None
    if payload.doctor_id:
        doctor = get_doctor(payload.doctor_id)
    if not doctor and consultation.get("doctor_id"):
        doctor = get_doctor(consultation["doctor_id"])

    doctor_name = doctor["name"] if doctor else "Doctor"

    if payload.action == "accept":
        consultation["status"] = "in_progress"
    elif payload.action == "reject":
        consultation["status"] = "rejected"
    elif payload.action == "complete":
        consultation["status"] = "completed"

    if payload.notes:
        existing_notes = consultation.get("doctor_notes")
        consultation["doctor_notes"] = f"{existing_notes}\n\n{payload.notes}" if existing_notes else payload.notes
        
        # Append doctor response directly to conversation_history for patient real-time chat
        history = consultation.get("conversation_history", [])
        history.append({
            "role": "doctor",
            "message": payload.notes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "doctor_name": doctor_name,
        })
        consultation["conversation_history"] = history

        # Add timeline event so patient sees the response
        add_timeline_event({
            "patient_id": consultation["patient_id"],
            "event_type": "DOCTOR_NOTE",
            "title": f"Response from {doctor_name}",
            "description": payload.notes,
            "consultation_id": consultation["id"],
        })

    save_consultation(consultation)
    return {"status": "ok", "consultation": consultation}


@router.post("/doctor/prescription")
async def issue_prescription(payload: PrescriptionReq):
    consultation = get_consultation(payload.consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    doctor = get_doctor(payload.doctor_id)
    doctor_name = doctor["name"] if doctor else "Doctor"

    prescription = save_prescription({
        "consultation_id": payload.consultation_id,
        "doctor_id": payload.doctor_id,
        "patient_id": consultation["patient_id"],
        "diagnosis": payload.diagnosis,
        "medicines": payload.medicines,
        "instructions": payload.instructions or "",
        "follow_up_date": payload.follow_up_date,
        "doctor_name": doctor_name,
    })

    # Format prescription into consultation doctor_notes so patient sees it in chat
    med_list = "\n".join([f"• {m.get('name')} — Dose: {m.get('dose', m.get('dosage',''))} | Freq: {m.get('frequency','')} | Duration: {m.get('duration','')}" for m in payload.medicines])
    rx_note = f"📋 PRESCRIPTION ISSUED BY {doctor_name.upper()}\n\nDiagnosis: {payload.diagnosis}\n\nPrescribed Medicines:\n{med_list}"
    if payload.instructions:
        rx_note += f"\n\nSpecial Instructions: {payload.instructions}"
    
    existing_notes = consultation.get("doctor_notes")
    consultation["doctor_notes"] = f"{existing_notes}\n\n{rx_note}" if existing_notes else rx_note
    consultation["status"] = "completed"

    # Append prescription directly into conversation_history for patient real-time chat view
    history = consultation.get("conversation_history", [])
    history.append({
        "role": "doctor",
        "message": rx_note,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "doctor_name": doctor_name,
    })
    consultation["conversation_history"] = history

    save_consultation(consultation)



    # Add timeline event so patient sees the prescription
    add_timeline_event({
        "patient_id": consultation["patient_id"],
        "event_type": "PRESCRIPTION",
        "title": f"Prescription from {doctor_name}",
        "description": f"Diagnosis: {payload.diagnosis}. "
                       f"Medicines: {', '.join(m.get('name','') for m in payload.medicines)}. "
                       f"Instructions: {payload.instructions}",
        "consultation_id": consultation["id"],
        "prescription_id": prescription["id"],
    })

    logger.info("Prescription issued: rx_id=%d consultation=%d", prescription["id"], consultation["id"])
    return prescription


@router.get("/doctor/patients")
async def doctor_patients():
    """List all patients."""
    return get_all_patients()


# ── Init ──────────────────────────────────────────────────────────────────────

def init_json_store():
    """Seed default data on startup."""
    seed_defaults()
    logger.info("JSON file store initialised at backend/data/")
