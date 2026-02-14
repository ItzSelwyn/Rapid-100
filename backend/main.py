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

def safe(obj):
    if obj is None:
        return ""
    return str(obj).encode("utf-8", "ignore").decode("utf-8")

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
SILENCE_TIMEOUT = 1.8

buffer = b''
last_audio_time = time.time()
call_transcript = ""

# Twilio chunk timer
twilio_last_process = time.time()
TWILIO_CHUNK_SECONDS = 3.0


# ---------------- Processing Function ----------------
def process_audio(audio_bytes):
    global call_transcript

    if not audio_bytes:
        return

    try:
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

        # ---- FAST CAPTION (instant UI feedback) ----
        live_text = transcriber.transcribe_live("temp.wav")

        if live_text.strip():
            asyncio.create_task(manager.broadcast({
                "transcript": safe(call_transcript + " " + live_text),
                "type": "analyzing",
                "severity": "low",
                "department": "processing",
                "risks": []
            }))

        # ---- FINAL ACCURATE TRANSCRIPTION ----
        text = transcriber.transcribe_final("temp.wav")
        text = language.normalize(text)

        print("FINAL:", text)

        if not text.strip():
            return

        call_transcript += " " + text

        category = classifier.predict(call_transcript)
        severity = severity_engine.score(call_transcript)
        entities = extractor.extract(call_transcript)

        summary = summarizer.build_summary(call_transcript, category, severity, entities)
        department = dispatcher.route(category)

        notify(department, summary)

        asyncio.create_task(manager.broadcast({
            "transcript": safe(call_transcript),
            "type": safe(category),
            "severity": safe(severity),
            "department": safe(department),
            "risks": [safe(r) for r in entities.get("risks", [])]
        }))

    except Exception:
        print("\n====== PROCESS ERROR ======")
        traceback.print_exc()
        print("===========================")

# ---------------- Local Mic WebSocket ----------------
@app.websocket("/audio")
async def audio_stream(ws: WebSocket):
    global buffer, last_audio_time, call_transcript

    await ws.accept()
    print("Client connected")

    try:
        while True:
            try:
                chunk = await asyncio.wait_for(ws.receive_bytes(), timeout=0.2)
                buffer += chunk
                last_audio_time = time.time()

            except asyncio.TimeoutError:
                if buffer and (time.time() - last_audio_time > SILENCE_TIMEOUT):
                    process_audio(buffer)
                    buffer = b''

    except WebSocketDisconnect:
        print("\nCaller disconnected")

    finally:
        buffer = b''
        call_transcript = ""
        print("Call ended\n")


# ---------------- Dashboard WebSocket ----------------
@app.websocket("/live")
async def live_dashboard(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        manager.disconnect(ws)


# ---------------- Twilio Phone Call Stream ----------------
@app.websocket("/twilio-media")
async def twilio_media(ws: WebSocket):
    global buffer, last_audio_time, twilio_last_process, call_transcript

    await ws.accept()
    print("Twilio call connected")

    try:
        while True:
            msg = await ws.receive_json()
            event = msg.get("event")

            if event == "start":
                print("Twilio stream started")
                buffer = b''
                call_transcript = ""
                twilio_last_process = time.time()

                # 🔔 tell dashboard call started
                await manager.broadcast({
                    "event": "call_started"
                })

                continue

            if event == "connected":
                continue

            if event == "stop":
                print("Twilio call ended")
                process_audio(buffer)

                await manager.broadcast({
                    "event": "call_ended"
                })

                break

            if event == "media":
                payload = msg["media"]["payload"]

                ulaw = base64.b64decode(payload)
                pcm = audioop.ulaw2lin(ulaw, 2)
                pcm = audioop.ratecv(pcm, 2, 1, 8000, 16000, None)[0]

                buffer += pcm
                last_audio_time = time.time()

                # ⬇️ NEW: process every few seconds
                if time.time() - twilio_last_process > TWILIO_CHUNK_SECONDS:
                    print("Processing Twilio audio chunk...")
                    process_audio(buffer)
                    buffer = b''
                    twilio_last_process = time.time()

    except Exception as e:
        print("Twilio disconnected:", e)
