from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter()

@router.post("/incoming-call")
async def incoming_call(request: Request):

    # IMPORTANT: use NGROK host (not localhost)
    host = request.headers.get("x-forwarded-host", request.headers["host"])

    ws_url = f"wss://{host}/twilio-media"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Connecting you to emergency AI assistant</Say>
    <Connect>
        <Stream url="{ws_url}" />
    </Connect>
</Response>
"""

    return Response(content=twiml, media_type="application/xml")
