from langdetect import detect
from deep_translator import GoogleTranslator

class LanguageProcessor:

    def normalize(self, text: str) -> str:
        try:
            lang = detect(text)
            if lang != "en":
                text = GoogleTranslator(source='auto', target='en').translate(text)
        except:
            pass

        return text.lower()
