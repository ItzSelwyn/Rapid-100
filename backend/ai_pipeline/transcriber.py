from faster_whisper import WhisperModel

class Transcriber:

    def __init__(self):
        # Force CPU — no CUDA required
        self.live_model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8"
        )

        self.final_model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def transcribe_live(self, path):
        segments, _ = self.live_model.transcribe(
            path,
            beam_size=1,
            vad_filter=True
        )
        return " ".join([seg.text for seg in segments])

    def transcribe_final(self, path):
        segments, _ = self.final_model.transcribe(
            path,
            beam_size=5,
            vad_filter=True
        )
        return " ".join([seg.text for seg in segments])
