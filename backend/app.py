"""
ArogyaMitra AI — Main FastAPI Application

Agentic AI Healthcare Assistant
---------------------------------
The AI assists. The doctor decides.

Key guarantees:
  ✓ AI does NOT diagnose patients
  ✓ AI does NOT prescribe medicines
  ✓ AI does NOT determine risk levels
  ✓ The doctor is the final decision-maker

Routes:
  POST /patient/register   — Register new patient
  POST /patient/chat       — Text conversation with AI
  POST /patient/voice      — Voice conversation with AI
  POST /patient/report     — Upload medical report (OCR + AI explanation)
  POST /patient/image      — Upload medical image (AI vision analysis)
  GET  /patient/timeline   — Patient health timeline
  POST /doctor/register    — Register new doctor
  POST /doctor/login       — Doctor authentication
  POST /doctor/consultation — Take consultation action
  POST /doctor/prescription — Issue prescription
  GET  /doctor/consultations — Doctor's consultation list
  GET  /health             — Health check

Docs: http://localhost:8000/docs (Swagger UI)
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import init_db

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Startup / Shutdown ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle: initialise DB on startup, clean up on shutdown."""
    logger.info("Starting ArogyaMitra AI — %s", settings.APP_VERSION)
    logger.info("Initialising database...")
    await init_db()
    logger.info("Database ready.")
    await _seed_demo_data()
    logger.info("ArogyaMitra AI is running. Swagger docs at /docs")
    logger.info("AI Mode: %s", "Gemini enabled" if settings.GEMINI_API_KEY else "Demo mode (no GEMINI_API_KEY)")
    yield
    logger.info("ArogyaMitra AI shutting down.")


async def _seed_demo_data() -> None:
    """
    Seed one demo doctor and one demo patient so the API can be tested immediately
    without manual data entry.
    """
    from backend.database import AsyncSessionLocal
    from backend.models.doctor import Doctor
    from backend.models.patient import Patient
    from backend.utils.auth import hash_password
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        try:
            # Seed demo doctors
            result = await db.execute(
                select(Doctor).where(Doctor.email == "dr.demo@arogya.ai")
            )
            if not result.scalars().first():
                demo_doctor = Doctor(
                    name="Dr. Priya Sharma",
                    email="dr.demo@arogya.ai",
                    phone="+919876543210",
                    specialization="General Physician",
                    qualification="MBBS, MD (General Medicine)",
                    registration_number="MCI-DEMO-001",
                    hashed_password=hash_password("demo1234"),
                    is_available=True,
                    is_active=True,
                    bio="Demo doctor for ArogyaMitra AI testing.",
                    hospital_affiliation="ArogyaMitra Demo Hospital",
                )
                db.add(demo_doctor)

            result_vikram = await db.execute(
                select(Doctor).where(Doctor.email == "dr.vikram@example.com")
            )
            if not result_vikram.scalars().first():
                vikram_doctor = Doctor(
                    name="Dr. Vikram Patel",
                    email="dr.vikram@example.com",
                    phone="+919876543211",
                    specialization="Cardiologist",
                    qualification="MBBS, MD, DM (Cardiology)",
                    registration_number="MCI-VIKRAM-002",
                    hashed_password=hash_password("password123"),
                    is_available=True,
                    is_active=True,
                    bio="Lead Cardiologist at ArogyaMitra Healthcare.",
                    hospital_affiliation="City Heart Care Hospital",
                )
                db.add(vikram_doctor)
                logger.info("Demo doctor seeded: dr.vikram@example.com / password123")

            # Seed demo patient
            result = await db.execute(
                select(Patient).where(Patient.phone == "+910000000001")
            )
            if not result.scalars().first():
                demo_patient = Patient(
                    name="Ravi Kumar",
                    phone="+910000000001",
                    email="ravi.demo@arogya.ai",
                    age=35,
                    gender="Male",
                    blood_group="O+",
                    allergies="None known",
                    known_conditions="None",
                    current_medications="None",
                )
                db.add(demo_patient)
                logger.info("Demo patient seeded: id will be auto-assigned")

            await db.commit()
        except Exception as exc:
            logger.error("Failed to seed demo data: %s", exc)
            await db.rollback()


# ── Application ────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ────────────────────────────────────────────────────────────────────
# Using JSON file-backed API only (replaces old SQLAlchemy routes)
from backend.api.json_api import router as json_router, init_json_store
from backend.api.twilio_voice import router as twilio_router
from backend.api.web_call import router as web_call_router
from backend.api.exotel_voice import router as exotel_router

init_json_store()

import os
from fastapi.staticfiles import StaticFiles

uploads_dir = os.path.join(os.path.dirname(__file__), "data", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(json_router)
app.include_router(twilio_router)
app.include_router(web_call_router)
app.include_router(exotel_router)




# ── Root & Health ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"], summary="Application info")
async def root() -> dict:
    """Returns application name, version, and Swagger docs URL."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "description": settings.APP_DESCRIPTION,
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "ai_mode": "enabled" if settings.GEMINI_API_KEY else "demo (set GEMINI_API_KEY to enable AI)",
        "safety_notice": settings.AI_DISCLAIMER,
    }


@app.get("/health", tags=["Info"], summary="Health check")
async def health_check() -> dict:
    """Lightweight health check endpoint for monitoring and load balancers."""
    from backend.database import engine
    db_status = "unknown"
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "healthy"
    except Exception as exc:
        db_status = f"error: {exc}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "ai_configured": bool(settings.GEMINI_API_KEY),
        "version": settings.APP_VERSION,
    }


# ── Global exception handler ───────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Catch-all handler that returns a structured error response."""
    logger.error("Unhandled exception: %s %s — %s", request.method, request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again.",
            "path": str(request.url),
        },
    )
