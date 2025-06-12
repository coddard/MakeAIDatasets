import re
import logging
import os
from typing import List
from fasttext import FastText

logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self, lang_model: FastText._FastText = None):
        self.lang_model = lang_model
        self.min_confidence = float(os.getenv("MIN_ENGLISH_CONFIDENCE", 0.7))
        
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
        """Determine if text is English with confidence threshold"""
        if not self.lang_model or not text.strip():
            return False
        try:
            sample = text if len(text) < 500 else text[:250] + text[-250:]
            predictions = self.lang_model.predict(
                sample.replace("\n", " "),
                k=1
            )
            return (predictions[0][0] == '__label__en' and 
                    predictions[1][0] >= self.min_confidence)
        except Exception as e:
            logger.warning(f"Language detection error: {str(e)}")
            return False
    
    def filter_english(self, lines: List[str]) -> List[str]:
        """Filter non-English text from line list"""
        return [line for line in lines if self.is_english(line)]