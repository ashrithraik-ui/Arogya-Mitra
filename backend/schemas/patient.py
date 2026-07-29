"""
ArogyaMitra AI — Patient Pydantic Schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ── Registration / Update ─────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    """Create a new patient record."""
    name: str = Field(..., min_length=1, max_length=100, examples=["Ravi Kumar"])
    phone: str = Field(..., min_length=7, max_length=20, examples=["+919876543210"])
    email: Optional[str] = Field(None, examples=["ravi@example.com"])
    age: Optional[int] = Field(None, ge=0, le=150, examples=[35])
    gender: Optional[str] = Field(None, examples=["Male"])
    blood_group: Optional[str] = Field(None, examples=["O+"])
    allergies: Optional[str] = Field(None, examples=["Penicillin, Dust"])
    known_conditions: Optional[str] = Field(None, examples=["Type 2 Diabetes, Hypertension"])
    current_medications: Optional[str] = Field(None, examples=["Metformin 500mg"])


class PatientUpdate(BaseModel):
    """Partial update for a patient record."""
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    known_conditions: Optional[str] = None
    current_medications: Optional[str] = None


class PatientResponse(BaseModel):
    """Patient data returned to the client."""
    id: int
    name: str
    phone: str
    email: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    blood_group: Optional[str]
    allergies: Optional[str]
    known_conditions: Optional[str]
    current_medications: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Patient sends a chat message to the AI conversation agent."""
    patient_id: int = Field(..., examples=[1])
    consultation_id: Optional[int] = Field(
        None,
        description="Existing consultation ID to continue. If None, a new consultation is created.",
        examples=[None],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        examples=["I have a headache and fever since yesterday."],
    )


class ChatResponse(BaseModel):
    """AI response returned to the patient after processing their message."""
    consultation_id: int
    ai_response: str
    follow_up_question: Optional[str] = None
    is_summary_ready: bool = False
    disclaimer: str

    model_config = {"from_attributes": True}


# ── Voice ─────────────────────────────────────────────────────────────────────

class VoiceResponse(BaseModel):
    """Response after processing a voice audio file."""
    consultation_id: int
    transcribed_text: str
    ai_response: str
    follow_up_question: Optional[str] = None
    audio_response_path: Optional[str] = None
    disclaimer: str


# ── Report OCR ───────────────────────────────────────────────────────────────

class ReportAnalysisResponse(BaseModel):
    """Response after OCR + AI explanation of a medical report."""
    consultation_id: int
    extracted_text: str
    simplified_explanation: str
    key_findings: list[str] = []
    disclaimer: str


# ── Medical Image Vision ──────────────────────────────────────────────────────

class ImageAnalysisResponse(BaseModel):
    """Response after AI vision analysis of a medical image."""
    consultation_id: int
    observations: str
    key_findings: list[str] = []
    forwarded_to_doctor: bool = True
    disclaimer: str
