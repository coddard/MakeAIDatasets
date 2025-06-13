import pytest
from src.processors.txt_processor import process_txt
from pathlib import Path

def test_process_txt():
    test_file = Path('input/test.txt')
    text = process_txt(test_file)
    assert isinstance(text, str)
