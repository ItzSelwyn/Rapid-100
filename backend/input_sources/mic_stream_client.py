import sounddevice as sd
import websocket
import webrtcvad
import time
import threading

WS_URL = "ws://127.0.0.1:8000/audio"
RATE = 16000
FRAME_DURATION = 30  # ms
FRAME_SIZE = int(RATE * FRAME_DURATION / 1000)

vad = webrtcvad.Vad(2)
running = True
ws = None


def is_speech(frame_bytes):
    return vad.is_speech(frame_bytes, RATE)


def on_audio(indata, frames, time_info, status):
    global ws, running

    if not running:
        return

    audio_bytes = indata[:, 0].tobytes()

    # send only speech
    if is_speech(audio_bytes):
        try:
            ws.send(audio_bytes, opcode=websocket.ABNF.OPCODE_BINARY)
        except:
            running = False


def stream_audio():
    with sd.InputStream(
        samplerate=RATE,
        channels=1,
        dtype="int16",
        blocksize=FRAME_SIZE,
        callback=on_audio
    ):
        print("🎤 Speak naturally... pause to process (Ctrl+C to stop)")
        while running:
            time.sleep(0.1)


# connect with retry
while True:
    try:
        ws = websocket.WebSocket()
        ws.connect(WS_URL)
        break
    except:
        print("Waiting for server...")
        time.sleep(1)


try:
    t = threading.Thread(target=stream_audio)
    t.start()

    while t.is_alive():
        time.sleep(0.2)

except KeyboardInterrupt:
    running = False

finally:
    if ws:
        ws.close()
    print("Disconnected cleanly")
