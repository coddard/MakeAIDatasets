import pytest
from src.processors.text_cleaner import TextCleaner

def test_clean_text():
    cleaner = TextCleaner()
    raw_text = 'This is a test\n\nAnother test line.'
    cleaned = cleaner.clean_text(raw_text)
    assert len(cleaned) > 0

def test_is_english():
    cleaner = TextCleaner()
    assert cleaner.is_english('This is a test.')
    assert not cleaner.is_english('Esto es una prueba.')
