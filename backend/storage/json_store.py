"""
ArogyaMitra AI — JSON File Storage
Stores all data as JSON files on the local machine for reliable persistence.
Files are saved under backend/data/.
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(filename: str) -> list[dict]:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(filename: str, data: list[dict]):
    _ensure_dir()
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)


def _next_id(records: list[dict]) -> int:
    if not records:
        return 1
    return max(r.get("id", 0) for r in records) + 1


# ── Patients ──────────────────────────────────────────────────────────────────

def get_all_patients() -> list[dict]:
    return _load("patients.json")


def get_patient(patient_id: int) -> Optional[dict]:
    for p in _load("patients.json"):
        if p["id"] == patient_id:
            return p
    return None


def get_patient_by_phone(phone: str) -> Optional[dict]:
    for p in _load("patients.json"):
        if p.get("phone") == phone:
            return p
    return None


def save_patient(data: dict) -> dict:
    patients = _load("patients.json")
    if "id" not in data:
        data["id"] = _next_id(patients)
    data["created_at"] = data.get("created_at", datetime.now(timezone.utc).isoformat())
    # Update if exists, else append
    for i, p in enumerate(patients):
        if p["id"] == data["id"]:
            patients[i] = data
            _save("patients.json", patients)
            return data
    patients.append(data)
    _save("patients.json", patients)
    return data


# ── Doctors ───────────────────────────────────────────────────────────────────

def get_all_doctors() -> list[dict]:
    return _load("doctors.json")


def get_doctor(doctor_id: int) -> Optional[dict]:
    for d in _load("doctors.json"):
        if d["id"] == doctor_id:
            return d
    return None


def get_doctor_by_email(email: str) -> Optional[dict]:
    for d in _load("doctors.json"):
        if d.get("email", "").lower() == email.lower():
            return d
    return None


def save_doctor(data: dict) -> dict:
    doctors = _load("doctors.json")
    if "id" not in data:
        data["id"] = _next_id(doctors)
    for i, d in enumerate(doctors):
        if d["id"] == data["id"]:
            doctors[i] = data
            _save("doctors.json", doctors)
            return data
    doctors.append(data)
    _save("doctors.json", doctors)
    return data


# ── Consultations ─────────────────────────────────────────────────────────────

def get_all_consultations() -> list[dict]:
    return _load("consultations.json")


def get_consultation(consultation_id: int) -> Optional[dict]:
    for c in _load("consultations.json"):
        if c["id"] == consultation_id:
            return c
    return None


def get_consultations_by_patient(patient_id: int) -> list[dict]:
    return [c for c in _load("consultations.json") if c.get("patient_id") == patient_id]


def get_consultations_by_doctor(doctor_id: int) -> list[dict]:
    return [c for c in _load("consultations.json") if c.get("doctor_id") == doctor_id]


def get_active_consultation(patient_id: int) -> Optional[dict]:
    """Get the most recent consultation for a patient."""
    patient_cons = [
        c for c in _load("consultations.json")
        if c.get("patient_id") == patient_id
    ]
    if patient_cons:
        return max(patient_cons, key=lambda x: x.get("id", 0))
    return None



def save_consultation(data: dict) -> dict:
    consultations = _load("consultations.json")
    if "id" not in data:
        data["id"] = _next_id(consultations)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    if "created_at" not in data:
        data["created_at"] = data["updated_at"]
    for i, c in enumerate(consultations):
        if c["id"] == data["id"]:
            consultations[i] = data
            _save("consultations.json", consultations)
            return data
    consultations.append(data)
    _save("consultations.json", consultations)
    return data


# ── Prescriptions ─────────────────────────────────────────────────────────────

def get_all_prescriptions() -> list[dict]:
    return _load("prescriptions.json")


def get_prescriptions_by_patient(patient_id: int) -> list[dict]:
    return [p for p in _load("prescriptions.json") if p.get("patient_id") == patient_id]


def get_prescriptions_by_consultation(consultation_id: int) -> list[dict]:
    return [p for p in _load("prescriptions.json") if p.get("consultation_id") == consultation_id]


def save_prescription(data: dict) -> dict:
    prescriptions = _load("prescriptions.json")
    if "id" not in data:
        data["id"] = _next_id(prescriptions)
    data["created_at"] = data.get("created_at", datetime.now(timezone.utc).isoformat())
    for i, p in enumerate(prescriptions):
        if p["id"] == data["id"]:
            prescriptions[i] = data
            _save("prescriptions.json", prescriptions)
            return data
    prescriptions.append(data)
    _save("prescriptions.json", prescriptions)
    return data


# ── Timeline Events ───────────────────────────────────────────────────────────

def get_timeline(patient_id: int) -> list[dict]:
    events = [e for e in _load("timeline.json") if e.get("patient_id") == patient_id]
    return sorted(events, key=lambda x: x.get("created_at", ""), reverse=True)


def add_timeline_event(data: dict) -> dict:
    events = _load("timeline.json")
    if "id" not in data:
        data["id"] = _next_id(events)
    data["created_at"] = data.get("created_at", datetime.now(timezone.utc).isoformat())
    events.append(data)
    _save("timeline.json", events)
    return data


# ── Seed Default Data ─────────────────────────────────────────────────────────

def seed_defaults():
    """Seed default doctors and patients if they don't exist."""
    _ensure_dir()

    # Seed doctors
    if not get_doctor_by_email("dr.demo@arogya.ai"):
        save_doctor({
            "name": "Dr. Priya Sharma",
            "email": "dr.demo@arogya.ai",
            "phone": "+919876543210",
            "specialization": "General Physician",
            "qualification": "MBBS, MD (General Medicine)",
            "password": "demo1234",
            "is_available": True,
        })
        logger.info("Seeded doctor: dr.demo@arogya.ai / demo1234")

    if not get_doctor_by_email("dr.vikram@example.com"):
        save_doctor({
            "name": "Dr. Vikram Patel",
            "email": "dr.vikram@example.com",
            "phone": "+919876543211",
            "specialization": "Cardiologist",
            "qualification": "MBBS, MD, DM (Cardiology)",
            "password": "password123",
            "is_available": True,
        })
        logger.info("Seeded doctor: dr.vikram@example.com / password123")

    # Seed patient
    if not get_patient_by_phone("+910000000001"):
        save_patient({
            "name": "Ravi Kumar",
            "phone": "+910000000001",
            "age": 35,
            "gender": "Male",
            "blood_group": "O+",
            "allergies": "None",
            "known_conditions": "",
            "current_medications": "",
        })
        logger.info("Seeded patient: Ravi Kumar / +910000000001")

    logger.info("JSON data directory: %s", DATA_DIR)
