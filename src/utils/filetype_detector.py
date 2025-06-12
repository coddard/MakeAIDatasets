from pathlib import Path
import mimetypes

def detect_file_type(file_path: Path) -> str:
    """Returns the file type based on extension and mime type."""
    mime, _ = mimetypes.guess_type(str(file_path))
    ext = file_path.suffix.lower()
    if ext == ".pdf" or (mime and "pdf" in mime):
        return "pdf"
    if ext == ".epub" or (mime and "epub" in mime):
        return "epub"
    return "unknown"
