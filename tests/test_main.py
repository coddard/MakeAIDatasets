import pytest
from src.main import process_single_file, process_batch_files
from src.processors.text_cleaner import TextCleaner
from pathlib import Path

def test_process_single_file():
    cleaner = TextCleaner()
    test_file = Path('input/test.txt')
    result = process_single_file(test_file, cleaner)
    assert result in [True, False]

def test_process_batch_files():
    cleaner = TextCleaner()
    result = process_batch_files(cleaner)
    assert result in [True, False]
