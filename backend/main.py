from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import wave
import io
import time
import traceback
import base64
import audioop

# ---------------- AI Modules ----------------
from backend.ai_pipeline.transcriber import Transcriber
from backend.ai_pipeline.classifier import EmergencyClassifier
from backend.ai_pipeline.severity_engine import SeverityEngine
from backend.ai_pipeline.language_processor import LanguageProcessor
from backend.ai_pipeline.entity_extractor import EntityExtractor
from backend.ai_pipeline.summarizer import Summarizer
from backend.routing.dispatcher import Dispatcher
from backend.routing.notifier import notify
from backend.websocket.live_updates import manager
from backend.input_sources.twilio_call import router as twilio_router
# --------------------------------------------

app = FastAPI()
app.include_router(twilio_router)

@app.get("/")
def home():
    return {"status": "RAPID-100 backend running"}


# ================= LIVE INCIDENT MEMORY =================
current_incident = {
    "active": False,
    "transcript": "",
    "type": None,
    "severity": None,
    "department": None,
    "risks": [],
    "victims": None,
    "location": None
}
# ========================================================


# Initialize AI components
transcriber = Transcriber()
classifier = EmergencyClassifier()
severity_engine = SeverityEngine()
language = LanguageProcessor()
extractor = EntityExtractor()
summarizer = Summarizer()
dispatcher = Dispatcher()

# Audio state
SAMPLE_RATE = 16000
buffer = b''
call_transcript = ""

# Twilio chunk timer
twilio_last_process = time.time()
TWILIO_CHUNK_SECONDS = 3.0


# ================= PROCESS AUDIO =================
def process_audio(audio_bytes):
    global call_transcript, current_incident

    try:
        # convert raw PCM → wav
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_bytes)

        wav_io.seek(0)
        with open("temp.wav", "wb") as f:
            f.write(wav_io.read())

        print("\nProcessing speech segment...")

        # ---- TRANSCRIBE ----
        text = transcriber.transcribe_live("temp.wav")
        text = language.normalize(text)

        print("FINAL:", text)

        if not text or not text.strip():
            return

        # accumulate conversation
        call_transcript += " " + text

        # ---- AI PIPELINE ----
        category = classifier.predict(call_transcript)
        severity = severity_engine.score(call_transcript)
        entities = extractor.extract(call_transcript)
        department = dispatcher.route(category)

        summary = summarizer.build_summary(call_transcript, category, severity, entities)
        notify(department, summary)

        # ===== STORE STATE (IMPORTANT) =====
        current_incident.update({
            "active": True,
            "transcript": call_transcript,
            "type": category,
            "severity": severity,
            "department": department,
            "risks": entities.get("risks", []),
            "victims": entities.get("victims"),
            "location": entities.get("location_hint")
        })

        # broadcast FULL state
        asyncio.create_task(manager.broadcast(current_incident))

    except Exception:
        print("\n====== PROCESS ERROR ======")
        traceback.print_exc()
        print("===========================")


# ================= DASHBOARD SOCKET =================
@app.websocket("/live")
async def live_dashboard(ws: WebSocket):
    await manager.connect(ws)

    # send current state immediately when operator joins
    if current_incident["active"]:
        await ws.send_json(current_incident)

    try:
        while True:
            await ws.receive_text()
    except:
        manager.disconnect(ws)
        print("Dashboard disconnected")


# ================= TWILIO MEDIA STREAM =================
@app.websocket("/twilio-media")
async def twilio_media(ws: WebSocket):
    global buffer, call_transcript, twilio_last_process, current_incident

    await ws.accept()
    print("Twilio call connected")

    try:
        while True:
            msg = await ws.receive_json()
            event = msg.get("event")

            # ---- CALL START ----
            if event == "start":
                print("Twilio stream started")

                buffer = b''
                call_transcript = ""
                twilio_last_process = time.time()

                current_incident.update({
                    "active": True,
                    "transcript": "",
                    "type": None,
                    "severity": None,
                    "department": None,
                    "risks": [],
                    "victims": None,
                    "location": None
                })

                await manager.broadcast({"event": "call_started"})
                continue

            # ---- CALL END ----
            if event == "stop":
                print("Twilio call ended")

                process_audio(buffer)

                current_incident["active"] = False
                await manager.broadcast({"event": "call_ended"})
                break

            # ---- AUDIO ----
            if event == "media":
                payload = msg["media"]["payload"]

                ulaw = base64.b64decode(payload)
                pcm = audioop.ulaw2lin(ulaw, 2)
                pcm = audioop.ratecv(pcm, 2, 1, 8000, 16000, None)[0]

                buffer += pcm

                # process chunk every few seconds
                if time.time() - twilio_last_process > TWILIO_CHUNK_SECONDS:
                    print("Processing Twilio audio chunk...")
                    process_audio(buffer)
                    buffer = b''
                    twilio_last_process = time.time()

    except Exception as e:
        print("Twilio disconnected:", e)
