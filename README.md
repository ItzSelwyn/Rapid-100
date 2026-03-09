# 🚨 RAPID-100

Real-time AI for Priority Incident Dispatch — a decision-support system to assist emergency call operators by transcribing calls, extracting structured information, assessing severity, and suggesting routing.

---

**Contents**
- Overview
- Architecture
- Requirements
- Quick start (backend, frontend, ngrok)
- Development notes

---

## Overview

RAPID-100 is a prototype that demonstrates live-call transcription and automated triage using an AI pipeline. The repository contains a Python backend (FastAPI-based), a React/Vite frontend, and components for live audio inputs and model inference.

This README documents how to run the core pieces locally and lists missing files or secrets you will likely need to provide before the system is fully operational.

---

## Architecture (high level)

- Backend: FastAPI app at `backend/main.py` exposing REST and WebSocket endpoints for live updates and triage results.
- AI pipeline: `backend/ai_pipeline/` contains transcript, intent/severity, and summarization components.
- Input adapters: `input_sources/` contains modules for mic, file, and telephony inputs (Twilio helper present).
- Frontend: React app under `frontend/rapid-ui` served by Vite; connects to backend APIs / websockets to display live summaries and routing suggestions.

---

## Requirements

- Python 3.10+ (virtualenv recommended)
- Node.js 16+ / npm or yarn
- `requirements.txt` in repo root lists Python dependencies — install into a virtual environment.
- Optional: `ngrok` for exposing the local backend to the internet (for Twilio or remote testing).

Example (Windows PowerShell):

```powershell
python -m venv rapidenv
./rapidenv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Frontend:

```bash
cd frontend/rapid-ui
npm install
npm run dev
```

---

## Quick start — Backend (FastAPI)

1. Activate your Python virtual environment.
2. Ensure dependencies are installed: `pip install -r requirements.txt`.
3. Provide required environment variables (see "Missing files" below for `.env` example).
4. Run the API with uvicorn (from repo root):

```bash
uvicorn backend.main:app --reload
```

Notes:
- The FastAPI app exposes HTTP endpoints used by the frontend and may also provide WebSocket endpoints for live updates (see `backend/websocket/live_updates.py`).
- If your models require GPU or large weights (e.g., speech models), ensure model paths and any required environment variables are set.

---

## Quick start — Frontend (React / Vite)

1. From `frontend/rapid-ui` install Node deps: `npm install`.
2. Start dev server:

```bash
cd frontend/rapid-ui
npm run dev
```
---

## Expose backend with ngrok

1. Install ngrok and authenticate with your authtoken: `ngrok authtoken <your-token>`.
2. Start ngrok to forward to your local backend port (8000):

```bash
ngrok http 8000
```
3. Use the public forwarding URL shown by ngrok to configure Twilio

NOTE:- use ngrok to receive telephony webhooks (e.g., Twilio), configure the webhook URL in the provider dashboard.

---

## Developer notes & pointers

- The AI pipeline is split across `backend/ai_pipeline/` — each module (transcriber, classifier, summarizer, severity_engine) is intended to be testable independently.
- To wire things up quickly for frontend dev, consider mocking the backend responses with a small script that emits sample JSON over the same WebSocket endpoints.
- When testing telephony integrations, use ngrok to expose the backend and configure provider webhooks to the ngrok URL.

---

## Troubleshooting

- If the frontend cannot reach the backend: ensure `VITE_API_BASE_URL` or the API client points to `http://localhost:8000`.
- If model loading fails: check `MODEL_PATH`, install required model libraries, and verify GPU/CPU compatibility.
- If Twilio calls don’t arrive: confirm ngrok is running and the public URL is configured as the webhook.