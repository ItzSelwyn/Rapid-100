class Summarizer:

    def build_summary(self, text, category, severity, entities):

        return f"""
EMERGENCY REPORT
Type: {category.upper()}
Severity: {severity.upper()}

Details:
{text}

Detected Risks: {', '.join(entities['risks']) if entities['risks'] else 'None'}
Victims: {entities['victims'] if entities['victims'] else 'Unknown'}
Location Hint: {entities['location_hint'] if entities['location_hint'] else 'Unknown'}
"""
