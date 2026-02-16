class Summarizer:

    def build_summary(self, transcript, category, severity, entities):

        risks = ", ".join(entities.get("risks", [])) or "None"
        victims = entities.get("victims", "Unknown")
        location = entities.get("location", "Unknown")

        summary = f"""
EMERGENCY REPORT
Type: {category.upper()}
Severity: {severity.upper()}

Details:
{transcript}

Detected Risks: {risks}
Victims: {victims}
Location Hint: {location}
"""
        return summary.strip()
