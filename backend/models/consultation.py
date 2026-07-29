"""
ArogyaMitra AI — Consultation, Prescription, and Learning Record ORM Models
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
import enum


class ConsultationStatus(str, enum.Enum):
    PENDING = "pending"          # Waiting for doctor assignment
    ASSIGNED = "assigned"        # Doctor assigned, awaiting review
    IN_PROGRESS = "in_progress"  # Doctor actively reviewing
    COMPLETED = "completed"      # Prescription/notes sent
    REJECTED = "rejected"        # Doctor rejected / referred elsewhere
    REFERRED = "referred"        # Referred to hospital/specialist


class Consultation(Base):
    """A single patient consultation session managed by the AI and reviewed by a doctor."""

    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign keys
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[ConsultationStatus] = mapped_column(
        SAEnum(ConsultationStatus), default=ConsultationStatus.PENDING, nullable=False
    )

    # Chief complaint entered by patient
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Full conversation history stored as JSON string
    # Format: [{"role": "patient"|"ai", "message": "...", "timestamp": "..."}]
    conversation_history: Mapped[str | None] = mapped_column(Text, nullable=True, default="[]")

    # Structured follow-up question answers stored as JSON string
    follow_up_answers: Mapped[str | None] = mapped_column(Text, nullable=True, default="{}")

    # Structured AI-generated patient summary forwarded to doctor
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Additional observations from uploaded files
    ocr_extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    vision_observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Paths to uploaded files stored as JSON list
    uploaded_files: Mapped[str | None] = mapped_column(Text, nullable=True, default="[]")

    # Doctor's notes after review
    doctor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Referral information
    referral_hospital: Mapped[str | None] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="consultations")  # noqa: F821
    doctor: Mapped["Doctor | None"] = relationship("Doctor", back_populates="consultations")  # noqa: F821
    prescription: Mapped["Prescription | None"] = relationship(
        "Prescription", back_populates="consultation", uselist=False
    )
    learning_record: Mapped["LearningRecord | None"] = relationship(
        "LearningRecord", back_populates="consultation", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Consultation id={self.id} patient_id={self.patient_id} status={self.status}>"


class Prescription(Base):
    """Prescription issued by a doctor after reviewing an AI-assisted consultation."""

    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("consultations.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    doctor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False
    )
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )

    # Medicines as JSON: [{"name": "...", "dose": "...", "frequency": "...", "duration": "..."}]
    medicines: Mapped[str | None] = mapped_column(Text, nullable=True, default="[]")

    # Diagnosis note written by doctor
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Doctor instructions to patient
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Follow-up date if needed
    follow_up_date: Mapped[str | None] = mapped_column(String(30), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    consultation: Mapped["Consultation"] = relationship(
        "Consultation", back_populates="prescription"
    )

    def __repr__(self) -> str:
        return f"<Prescription id={self.id} consultation_id={self.consultation_id}>"


class LearningRecord(Base):
    """
    Anonymized record for the Doctor Learning Network.
    Stores AI summary + doctor summary + prescription for future reference.
    The AI does NOT use this to retrain any model automatically.
    """

    __tablename__ = "learning_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consultation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("consultations.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Anonymized AI summary (no patient PII)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Doctor's final summary / diagnosis note
    doctor_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Prescription data as JSON
    prescription_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Symptom keywords for future search
    symptom_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    consultation: Mapped["Consultation"] = relationship(
        "Consultation", back_populates="learning_record"
    )

    def __repr__(self) -> str:
        return f"<LearningRecord id={self.id} consultation_id={self.consultation_id}>"
