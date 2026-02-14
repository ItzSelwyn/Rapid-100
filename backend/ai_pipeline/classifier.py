CATEGORIES = ["medical", "fire", "crime", "accident", "disaster"]

class EmergencyClassifier:

    def predict(self, text):
        text = text.lower()

        if "not breathing" in text or "fainted" in text:
            return "medical"
        if "fire" in text or "smoke" in text:
            return "fire"
        if "knife" in text or "attack" in text:
            return "crime"
        if "crash" in text or "collision" in text:
            return "accident"

        return "unknown"
