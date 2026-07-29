"""
ArogyaMitra AI — Consultation Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.models.consultation import ConsultationStatus


class ConsultationSummaryResponse(BaseModel):
    """Compact consultation view used in list APIs."""
    id: int
    patient_id: int
    doctor_id: Optional[int]
    status: ConsultationStatus
    chief_complaint: Optional[str]
    ai_summary: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConsultationDetailResponse(BaseModel):
    """Full consultation detail including conversation and files."""
    id: int
    patient_id: int
    doctor_id: Optional[int]
    status: ConsultationStatus
    chief_complaint: Optional[str]
    conversation_history: Optional[str]   # JSON string
    follow_up_answers: Optional[str]      # JSON string
    ai_summary: Optional[str]
    ocr_extracted_text: Optional[str]
    vision_observations: Optional[str]
    uploaded_files: Optional[str]         # JSON list string
    doctor_notes: Optional[str]
    referral_hospital: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
