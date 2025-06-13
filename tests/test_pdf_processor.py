import pytest
from src.processors.pdf_processor import process_pdf
from pathlib import Path

def test_process_pdf():
    test_file = Path('input/test.pdf')
    text, ocr_used, metadata = process_pdf(test_file)
    assert isinstance(text, str)
    assert isinstance(ocr_used, bool)
    assert isinstance(metadata, dict)
