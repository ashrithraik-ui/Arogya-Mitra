"""
ArogyaMitra AI — Web Voice Call Handler
Provides a full-screen, WhatsApp-style Web Voice Call page at /call
Allows any device (phone, laptop, keypad phone browser) to call the AI Doctor.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Web Voice Call"])

@router.get("/call", response_class=HTMLResponse)
async def web_voice_call_page():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArogyaMitra AI — Live Voice Call</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 15px;
        }
        .call-card {
            background: rgba(30, 41, 59, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 28px;
            padding: 30px 24px;
            width: 100%;
            max-width: 420px;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .avatar-box {
            position: relative;
            width: 120px;
            height: 120px;
            margin: 0 auto 20px;
        }
        .avatar-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0d9488 0%, #2563eb 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 54px;
            color: white;
            box-shadow: 0 10px 30px rgba(13, 148, 136, 0.4);
            transition: transform 0.3s ease;
        }
        .pulse-ring {
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            border: 3px solid #0d9488;
            border-radius: 50%;
            animation: pulse 2s infinite;
            opacity: 0;
        }
        .calling .pulse-ring {
            opacity: 1;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.15); opacity: 0.3; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }
        .status-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            background: rgba(13, 148, 136, 0.2);
            color: #22d3ee;
            margin-bottom: 20px;
        }
        .transcript-box {
            background: rgba(15, 23, 42, 0.7);
            border-radius: 16px;
            padding: 15px;
            height: 220px;
            overflow-y: auto;
            text-align: left;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .msg-bubble {
            padding: 10px 14px;
            border-radius: 14px;
            margin-bottom: 10px;
            font-size: 14px;
            line-height: 1.4;
        }
        .msg-ai {
            background: rgba(13, 148, 136, 0.25);
            color: #67e8f9;
            border-bottom-left-radius: 4px;
        }
        .msg-user {
            background: rgba(37, 99, 235, 0.25);
            color: #93c5fd;
            margin-left: auto;
            border-bottom-right-radius: 4px;
            text-align: right;
        }
        .btn-call {
            width: 72px;
            height: 72px;
            border-radius: 50%;
            border: none;
            font-size: 28px;
            color: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }
        .btn-start {
            background: #059669;
        }
        .btn-start:hover {
            background: #10b981;
            transform: scale(1.05);
        }
        .btn-end {
            background: #dc2626;
        }
        .btn-end:hover {
            background: #ef4444;
            transform: scale(1.05);
        }
    </style>
</head>
<body>

<div class="call-card">
    <div class="avatar-box" id="avatarBox">
        <div class="pulse-ring"></div>
        <div class="avatar-circle">
            <i class="fa-solid fa-user-doctor"></i>
        </div>
    </div>

    <h4 class="fw-bold mb-1">ArogyaMitra AI Doctor</h4>
    <p class="text-secondary small mb-3">Live Voice Consultation</p>

    <div class="status-badge" id="statusBadge">Tap green call button to start</div>

    <div class="transcript-box" id="transcriptBox">
        <div class="text-center text-muted small mt-4">
            <i class="fa-solid fa-microphone-slash d-block fs-3 mb-2"></i>
            Click call button to connect with AI Doctor
        </div>
    </div>

    <div class="d-flex justify-content-center gap-4 align-items-center">
        <button class="btn-call btn-start" id="callBtn" onclick="toggleCall()">
            <i class="fa-solid fa-phone" id="callIcon"></i>
        </button>
    </div>
</div>

<script>
    let isCalling = false;
    let recognition = null;
    let synthesis = window.speechSynthesis;
    let consultationId = null;
    let callerNumber = "Web Caller";

    const statusBadge = document.getElementById("statusBadge");
    const transcriptBox = document.getElementById("transcriptBox");
    const callBtn = document.getElementById("callBtn");
    const callIcon = document.getElementById("callIcon");
    const avatarBox = document.getElementById("avatarBox");

    function toggleCall() {
        if (!isCalling) {
            startCall();
        } else {
            endCall();
        }
    }

    function startCall() {
        isCalling = true;
        callBtn.classList.remove("btn-start");
        callBtn.classList.add("btn-end");
        callIcon.className = "fa-solid fa-phone-slash";
        avatarBox.classList.add("calling");
        statusBadge.textContent = "🤖 Connected — AI Doctor Speaking...";

        transcriptBox.innerHTML = "";
        
        const greeting = "Hello! I am ArogyaMitra AI health assistant. What health symptoms or problems are you facing today?";
        addMessage("ai", greeting);
        speakText(greeting);
    }

    function endCall() {
        isCalling = false;
        callBtn.classList.remove("btn-end");
        callBtn.classList.add("btn-start");
        callIcon.className = "fa-solid fa-phone";
        avatarBox.classList.remove("calling");
        statusBadge.textContent = "Call Ended";

        if (synthesis) synthesis.cancel();
        if (recognition) try { recognition.stop(); } catch(e){}
    }

    function speakText(text) {
        if (!isCalling) return;
        statusBadge.textContent = "🔊 AI Doctor Speaking...";
        
        if ('speechSynthesis' in window) {
            synthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.95;
            utterance.pitch = 1.0;

            utterance.onend = function() {
                if (isCalling) {
                    setTimeout(startListening, 800);
                }
            };

            synthesis.speak(utterance);
        } else {
            setTimeout(startListening, 1500);
        }
    }

    function startListening() {
        if (!isCalling) return;
        statusBadge.textContent = "🎤 Listening to you... Speak now!";

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Speech recognition not supported in this browser. Please use Chrome/Edge.");
            return;
        }

        if (recognition) try { recognition.abort(); } catch(e){}
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = function(event) {
            const userSpeech = event.results[0][0].transcript;
            if (userSpeech.trim()) {
                addMessage("user", userSpeech);
                sendToServer(userSpeech);
            } else {
                if (isCalling) setTimeout(startListening, 1000);
            }
        };

        recognition.onerror = function(event) {
            console.warn("STT Error:", event.error);
            if (isCalling && event.error !== 'aborted') {
                setTimeout(startListening, 1200);
            }
        };

        try {
            recognition.start();
        } catch(e) {
            console.error("STT Start Error:", e);
        }
    }

    async function sendToServer(userText) {
        if (!isCalling) return;
        statusBadge.textContent = "🧠 AI Doctor Thinking...";

        try {
            const res = await fetch("/call/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    caller_number: callerNumber,
                    message: userText,
                    consultation_id: consultationId
                })
            });

            if (res.ok) {
                const data = await res.json();
                consultationId = data.consultation_id;
                const aiResponse = data.ai_response || "Thank you. Your details have been sent to the doctor.";
                addMessage("ai", aiResponse);
                speakText(aiResponse);
            } else {
                speakText("I had trouble reaching the server. Please tell me your symptoms again.");
            }
        } catch (e) {
            console.error("Server Error:", e);
            speakText("Connection error. Please try speaking again.");
        }
    }

    function addMessage(role, text) {
        const div = document.createElement("div");
        div.className = `msg-bubble ${role === 'ai' ? 'msg-ai' : 'msg-user'}`;
        div.innerHTML = `<strong>${role === 'ai' ? '🤖 AI Doctor' : '🗣️ You'}:</strong> ${text}`;
        transcriptBox.appendChild(div);
        transcriptBox.scrollTop = transcriptBox.scrollHeight;
    }
</script>

</body>
</html>
"""
    return HTMLResponse(content=html_content)
