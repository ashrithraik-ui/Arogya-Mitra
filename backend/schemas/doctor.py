"""
ArogyaMitra AI — Doctor Pydantic Schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class DoctorLogin(BaseModel):
    email: str = Field(..., examples=["dr.sharma@hospital.com"])
    password: str = Field(..., min_length=6, examples=["secret123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    doctor_id: int
    name: str
    specialization: str


# ── Doctor management ─────────────────────────────────────────────────────────

class DoctorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Dr. Amit Sharma"])
    email: str = Field(..., examples=["dr.amit@hospital.com"])
    phone: Optional[str] = Field(None, examples=["+919876543210"])
    specialization: str = Field(..., examples=["General Physician"])
    qualification: Optional[str] = Field(None, examples=["MBBS, MD"])
    registration_number: Optional[str] = Field(None, examples=["MCI-123456"])
    password: str = Field(..., min_length=6, examples=["securepass"])
    bio: Optional[str] = None
    hospital_affiliation: Optional[str] = Field(None, examples=["Apollo Hospital"])


class DoctorResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    specialization: str
    qualification: Optional[str]
    registration_number: Optional[str]
    is_available: bool
    is_active: bool
    bio: Optional[str]
    hospital_affiliation: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Consultation actions ───────────────────────────────────────────────────────

class ConsultationActionRequest(BaseModel):
    """Doctor accepts, rejects, or calls the patient."""
    consultation_id: int = Field(..., examples=[1])
    action: str = Field(
        ...,
        description="One of: accept | reject | call",
        examples=["accept"],
    )
    notes: Optional[str] = Field(None, examples=["Accepting the consultation for review."])


class ConsultationActionResponse(BaseModel):
    consultation_id: int
    status: str
    message: str


# ── Prescription ──────────────────────────────────────────────────────────────

class MedicineItem(BaseModel):
    name: str = Field(..., examples=["Paracetamol"])
    dose: str = Field(..., examples=["500mg"])
    frequency: str = Field(..., examples=["Twice daily"])
    duration: str = Field(..., examples=["5 days"])
    instructions: Optional[str] = Field(None, examples=["After meals"])


class PrescriptionCreate(BaseModel):
    consultation_id: int = Field(..., examples=[1])
    diagnosis: str = Field(..., min_length=1, examples=["Viral fever with body ache"])
    medicines: list[MedicineItem] = Field(default_factory=list)
    instructions: Optional[str] = Field(
        None, examples=["Rest well, drink plenty of fluids, avoid cold food."]
    )
    follow_up_date: Optional[str] = Field(None, examples=["2026-08-10"])
    referral_hospital: Optional[str] = Field(None, examples=["Apollo Hospital Mumbai"])
    doctor_notes: Optional[str] = Field(None, examples=["Patient responded well to initial queries."])


class PrescriptionResponse(BaseModel):
    id: int
    consultation_id: int
    doctor_id: int
    patient_id: int
    diagnosis: Optional[str]
    medicines: Optional[str]   # JSON string
    instructions: Optional[str]
    follow_up_date: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
