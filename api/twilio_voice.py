"""
ArogyaMitra AI — Twilio Voice AI Call Handler

Handles incoming phone calls via Twilio Voice Webhooks (TwiML).
1. Incoming Call -> /voice/incoming -> Greets caller & listens for speech via TwiML <Gather input="speech">
2. Speech Transcribed -> /voice/respond -> Twilio sends SpeechResult -> AI generates clinical response -> Returns TwiML <Say> + next <Gather>
3. Conversation saved to patient timeline and forwarded to Doctor Dashboard.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse

from backend.storage.json_store import (
    get_patient_by_phone, save_patient,
    get_consultation, get_active_consultation, save_consultation,
    get_all_doctors, add_timeline_event
)
from backend.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Twilio Voice AI"])


def twiml_response(content: str) -> Response:
    """Helper to return valid TwiML XML response."""
    xml_str = f'<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n{content}\n</Response>'
    return Response(content=xml_str, media_type="application/xml")


@router.post("/incoming")
async def twilio_incoming_call(
    From: Optional[str] = Form(default="Unknown"),
    CallSid: Optional[str] = Form(default=None)
):
    """
    Twilio Webhook: Triggered when a phone call is received on your Twilio number.
    Greets the caller using TwiML <Say> and listens for speech input using <Gather>.
    """
    caller_phone = From or "+910000000001"
    logger.info("📞 Twilio Incoming Call from %s (CallSid: %s)", caller_phone, CallSid)

    # Get or create patient by phone number
    patient = get_patient_by_phone(caller_phone)
    if not patient:
        patient = save_patient({
            "name": f"Caller ({caller_phone[-4:] if len(caller_phone)>=4 else 'Patient'})",
            "phone": caller_phone,
            "age": 30,
            "gender": "Unknown"
        })

    patient_id = patient["id"]

    # Start new consultation for this call
    doctors = get_all_doctors()
    assigned_doc = doctors[0]["id"] if doctors else None

    greeting_text = (
        "Hello! I am ArogyaMitra A I health assistant. "
        "I am here to collect your health details for your doctor. "
        "Please tell me, what health symptoms or problems are you facing today?"
    )

    consultation = save_consultation({
        "patient_id": patient_id,
        "status": "assigned" if assigned_doc else "pending",
        "chief_complaint": "Phone Call Consultation",
        "conversation_history": [
            {
                "role": "ai",
                "message": greeting_text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "follow_up_answers": {},
        "ai_summary": "Incoming phone call consultation initiated.",
        "uploaded_files": [],
        "doctor_id": assigned_doc,
        "doctor_notes": None,
    })

    add_timeline_event({
        "patient_id": patient_id,
        "event_type": "CONSULTATION",
        "title": "Incoming Phone Call Consultation",
        "description": f"Call from {caller_phone}",
        "consultation_id": consultation["id"],
    })

    # Generate TwiML to speak greeting and gather caller speech
    action_url = f"/voice/respond?consultation_id={consultation['id']}&patient_id={patient_id}"

    twiml = f"""
        <Say voice="Polly.Aditi" language="en-IN">{greeting_text}</Say>
        <Gather input="speech" timeout="5" speechTimeout="auto" action="{action_url}" method="POST">
            <Say voice="Polly.Aditi" language="en-IN">Please speak your symptoms after the tone.</Say>
        </Gather>
        <Say voice="Polly.Aditi" language="en-IN">We did not receive any input. Goodbye!</Say>
    """
    return twiml_response(twiml)


@router.post("/respond")
async def twilio_respond_call(
    consultation_id: int,
    patient_id: int,
    SpeechResult: Optional[str] = Form(default=None),
    Confidence: Optional[str] = Form(default=None),
    From: Optional[str] = Form(default=None)
):
    """
    Twilio Webhook: Triggered when Twilio transcribes the caller's spoken speech.
    Receives SpeechResult -> Sends to Gemini AI -> Returns TwiML <Say> response + next <Gather>.
    """
    spoken_text = SpeechResult or ""
    logger.info("🗣️ Twilio STT Result: '%s' (Confidence: %s)", spoken_text, Confidence)

    consultation = get_consultation(consultation_id)
    if not consultation:
        twiml = '<Say voice="Polly.Aditi" language="en-IN">Consultation session expired. Goodbye!</Say>'
        return twiml_response(twiml)

    action_url = f"/voice/respond?consultation_id={consultation_id}&patient_id={patient_id}"

    if not spoken_text.strip():
        twiml = f"""
            <Say voice="Polly.Aditi" language="en-IN">I could not hear your response clearly.</Say>
            <Gather input="speech" timeout="5" speechTimeout="auto" action="{action_url}" method="POST">
                <Say voice="Polly.Aditi" language="en-IN">Please describe your symptoms again.</Say>
            </Gather>
            <Say voice="Polly.Aditi" language="en-IN">Thank you for calling ArogyaMitra. Goodbye!</Say>
        """
        return twiml_response(twiml)

    # 1. Save patient spoken message to consultation history
    history = consultation.get("conversation_history", [])
    history.append({
        "role": "patient",
        "message": spoken_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # Update chief complaint if first turn
    if len(history) <= 2:
        consultation["chief_complaint"] = spoken_text

    # 2. Get AI response from Gemini service
    try:
        ai_ack = await gemini_service.generate_ai_chat_response(
            user_message=spoken_text,
            chief_complaint=consultation.get("chief_complaint", spoken_text),
            follow_up_answers=consultation.get("follow_up_answers", {}),
            conversation_history=history[-6:],
        )
    except Exception as e:
        logger.error("Gemini error during voice call: %s", e)
        ai_ack = "Thank you for describing your symptoms."

    if not ai_ack:
        ai_ack = "Thank you for describing your symptoms."

    # Clean up response for smooth speech output
    clean_ai_response = ai_ack.replace("\n", " ").replace("*", "").strip()

    # 3. Save AI response to history
    history.append({
        "role": "ai",
        "message": clean_ai_response,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    consultation["conversation_history"] = history

    # 4. Update AI Summary for Doctor Dashboard
    summary_text = f"Phone Call Consultation Summary:\nChief Complaint: {consultation.get('chief_complaint', '')}\n\nCall Transcript:\n"
    for m in history:
        summary_text += f"- {m.get('role', 'patient').upper()}: {m.get('message', '')}\n"
    consultation["ai_summary"] = summary_text
    consultation["status"] = "in_progress"

    save_consultation(consultation)

    # 5. Check if summary is complete or conversation should continue
    is_complete = len(history) >= 8 or "forwarded to your doctor" in clean_ai_response.lower()

    if is_complete:
        closing_text = f"{clean_ai_response} Thank you for calling ArogyaMitra. Your health report has been forwarded to the doctor. Goodbye!"
        twiml = f'<Say voice="Polly.Aditi" language="en-IN">{closing_text}</Say>'
    else:
        twiml = f"""
            <Say voice="Polly.Aditi" language="en-IN">{clean_ai_response}</Say>
            <Gather input="speech" timeout="5" speechTimeout="auto" action="{action_url}" method="POST">
            </Gather>
            <Say voice="Polly.Aditi" language="en-IN">Thank you for calling ArogyaMitra. Goodbye!</Say>
        """

    return twiml_response(twiml)


@router.get("/setup", response_class=HTMLResponse)
async def twilio_setup_instructions():
    """Returns HTML instructions on how to link Twilio Voice with your ArogyaMitra server."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArogyaMitra AI — Twilio Voice Setup</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; max-width: 800px; margin: 0 auto; }
            h1 { color: #0d9488; }
            .card { background: #1e293b; padding: 1.5rem; border-radius: 1rem; margin-bottom: 1.5rem; border: 1px solid #334155; }
            code { background: #0f172a; color: #22d3ee; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-family: monospace; }
            .step-num { background: #0d9488; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 0.5rem; }
        </style>
    </head>
    <body>
        <h1>📞 ArogyaMitra Twilio Voice Setup</h1>
        <p>Follow these quick steps to connect any phone number to your AI Health Assistant via Twilio:</p>

        <div class="card">
            <h3><span class="step-num">1</span> Expose Local Backend Server</h3>
            <p>Twilio requires a public URL to reach your local server. Run ngrok on port 8000:</p>
            <code>npx ngrok http 8000</code>
            <p>Copy the HTTPS URL generated (e.g. <code>https://abc1234.ngrok-free.app</code>).</p>
        </div>

        <div class="card">
            <h3><span class="step-num">2</span> Configure Twilio Phone Number Webhook</h3>
            <p>Log in to your <a href="https://console.twilio.com/" target="_blank" style="color: #22d3ee;">Twilio Console</a> -> Active Numbers -> Select your number.</p>
            <p>Under <strong>Voice & Fax</strong> -> <strong>A Call Comes In</strong>:</p>
            <ul>
                <li>Set dropdown to: <code>Webhook</code></li>
                <li>Set URL to: <code>https://YOUR_NGROK_URL/voice/incoming</code></li>
                <li>Set HTTP Method to: <code>HTTP POST</code></li>
            </ul>
        </div>

        <div class="card">
            <h3><span class="step-num">3</span> Test Your AI Phone Call!</h3>
            <p>Call your Twilio Phone Number from any mobile device or landline.</p>
            <ul>
                <li>Twilio will answer automatically.</li>
                <li>AI will greet you in Indian English voice (Polly.Aditi).</li>
                <li>Describe your symptoms — Twilio converts your voice to text, Gemini processes it, and the AI speaks back to you over the call!</li>
                <li>All transcripts immediately appear on your Doctor Dashboard!</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html_content
