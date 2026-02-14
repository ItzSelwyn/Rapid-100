KEYWORDS = {
    "not breathing": 5,
    "unconscious": 5,
    "bleeding": 4,
    "fire spreading": 4,
    "weapon": 5,
    "trapped": 5,
    "help": 1
}

class SeverityEngine:

    def score(self, text):
        score = 0
        for word, value in KEYWORDS.items():
            if word in text:
                score += value

        if score >= 13:
            return "critical"
        if score >= 8:
            return "high"
        if score >= 4:
            return "medium"
        return "low"
