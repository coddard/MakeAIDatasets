import pytest
from pathlib import Path
from src.processors.epub_processor import process_epub

def test_process_epub_empty(tmp_path):
    # Create an empty epub file
    epub_path = tmp_path / "empty.epub"
    epub_path.write_bytes(b"")
    result = process_epub(epub_path)
    assert result == ""
