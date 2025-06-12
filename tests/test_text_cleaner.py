import pytest
from src.processors.text_cleaner.py import TextCleaner

class DummyLangModel:
    def predict(self, text, k=1):
        # Simulate English detection with high confidence
        return [['__label__en'], [0.95]]

def test_clean_text():
    cleaner = TextCleaner()
    raw = "Hello world!\n  \nShort\nThis is a test.   "
    cleaned = cleaner.clean_text(raw)
    assert cleaned == ["Hello world!", "This is a test."]

def test_is_english():
    cleaner = TextCleaner(lang_model=DummyLangModel())
    assert cleaner.is_english("This is an English sentence.")
    assert not cleaner.is_english("")

def test_filter_english():
    cleaner = TextCleaner(lang_model=DummyLangModel())
    lines = ["This is English.", ""]
    filtered = cleaner.filter_english(lines)
    assert filtered == ["This is English."]
