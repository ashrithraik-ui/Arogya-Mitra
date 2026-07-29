"""
ArogyaMitra AI — Health Timeline Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.models.timeline import TimelineEventType


class TimelineEventCreate(BaseModel):
    patient_id: int
    event_type: TimelineEventType
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    metadata_json: Optional[str] = "{}"
    consultation_id: Optional[int] = None
    file_path: Optional[str] = None
    event_date: Optional[datetime] = None


class TimelineEventResponse(BaseModel):
    id: int
    patient_id: int
    event_type: TimelineEventType
    title: str
    description: Optional[str]
    metadata_json: Optional[str]
    consultation_id: Optional[int]
    file_path: Optional[str]
    event_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class PatientTimelineResponse(BaseModel):
    patient_id: int
    total_events: int
    events: list[TimelineEventResponse]
