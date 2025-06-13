import pytest
from src.processors.epub_processor import process_epub
from pathlib import Path

def test_process_epub():
    test_file = Path('input/test.epub')
    text = process_epub(test_file)
    assert isinstance(text, str)
