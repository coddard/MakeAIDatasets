import pytest
from src.processors.html_processor import process_html
from pathlib import Path

def test_process_html():
    test_file = Path('input/test.html')
    text = process_html(test_file)
    assert isinstance(text, str)
