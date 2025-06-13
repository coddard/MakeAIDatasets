import pytest
from src.processors.docx_processor import process_docx
from pathlib import Path

def test_process_docx():
    test_file = Path('input/test.docx')
    text = process_docx(test_file)
    assert isinstance(text, str)
