import re

class EntityExtractor:

    def __init__(self):
        self.number_words = {
            "one":1,"two":2,"three":3,"four":4,"five":5,
            "six":6,"seven":7,"eight":8,"nine":9,"ten":10
        }

    def extract(self, text: str):
        text_lower = text.lower()

        return {
            "risks": self.extract_risks(text_lower),
            "victims": self.extract_victims(text_lower),
            "location": self.extract_location(text)
        }

    # -------- RISKS --------
    def extract_risks(self, text):
        risks = []
        keywords = [
            "fire","smoke","gas","weapon","knife","gun",
            "bleeding","unconscious","not breathing","accident","crash"
        ]

        for k in keywords:
            if k in text:
                risks.append(k)

        return list(set(risks))

    # -------- VICTIMS --------
    def extract_victims(self, text):
        # numeric victims
        num_match = re.findall(r'(\d+)\s+(people|persons|kids|children|adults|men|women|injured)', text)
        if num_match:
            return num_match[0][0]

        # word numbers
        for word, num in self.number_words.items():
            if f"{word} people" in text or f"{word} persons" in text:
                return str(num)

        # single victim indicators
        single_words = ["my friend","my brother","my sister","a man","a woman","a child","someone"]
        for s in single_words:
            if s in text:
                return "1"

        return "Unknown"

    # -------- LOCATION --------
    def extract_location(self, text):
        # address pattern (12/4 road, 23 street, 4th cross)
        addr = re.search(r'\d{1,4}[\/\-]?\d*\s+(street|st|road|rd|nagar|colony|avenue|ave|layout)', text, re.I)
        if addr:
            return addr.group(0)

        # near landmark
        near = re.search(r'(near|opposite|behind|beside)\s+([A-Za-z ]+)', text, re.I)
        if near:
            return near.group(0)

        # city detection (simple list — add your hackathon city)
        cities = ["coimbatore","chennai","salem","erode","madurai","trichy","tiruppur"]
        for city in cities:
            if city in text.lower():
                return city.title()

        return "Unknown"
