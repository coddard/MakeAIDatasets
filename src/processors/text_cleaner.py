import re
import logging
from typing import List
from lingua import Language, LanguageDetectorBuilder

logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self):
        self.detector = LanguageDetectorBuilder.from_languages(Language.ENGLISH).build()

    def clean_text(self, text: str) -> List[str]:
        """Normalize and clean raw text"""
        cleaned = []
        for line in text.splitlines():
            stripped = line.strip()
            if len(stripped) < 10:
                continue
            normalized = re.sub(r"\s+", " ", stripped)
            cleaned.append(normalized)
        return cleaned

    def is_english(self, text: str) -> bool:
        """Determine if text is English using Lingua"""
        if not text.strip():
            return False
        try:
            language = self.detector.detect_language_of(text)
            return language == Language.ENGLISH
        except Exception as e:
            logger.warning(f"Language detection error: {str(e)}")
            return False

    def filter_english(self, lines: List[str]) -> List[str]:
        """Filter non-English text from line list"""
        return [line for line in lines if self.is_english(line)]