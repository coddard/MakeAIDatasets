import pytest
from pathlib import Path
from src.processors.pdf_processor import process_pdf

def test_process_pdf_invalid(tmp_path):
    # Create an invalid PDF file
    pdf_path = tmp_path / "invalid.pdf"
    pdf_path.write_bytes(b"not a real pdf")
    text, ocr_used, meta = process_pdf(pdf_path)
    assert text == ""
    assert ocr_used is False or ocr_used is True  # Should not crash
    assert isinstance(meta, dict)
