import re

class EntityExtractor:

    def extract(self, text: str):
        victims = None

        # detect number of people
        nums = re.findall(r'\d+', text)
        if nums:
            victims = int(nums[0])

        location_keywords = ["road", "street", "bus stand", "school", "hospital", "building"]
        location = None

        for word in location_keywords:
            if word in text:
                location = word
                break

        risks = []
        danger_words = ["fire", "smoke", "bleeding", "weapon", "knife", "unconscious", "not breathing"]

        for d in danger_words:
            if d in text:
                risks.append(d)

        return {
            "victims": victims,
            "location_hint": location,
            "risks": risks
        }
