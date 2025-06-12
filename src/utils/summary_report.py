import logging
import json
from pathlib import Path

def generate_summary_report(input_dir: Path, output_dir: Path, meta_dir: Path):
    """Generate a report with summary statistics for processed files."""
    report = {
        "total_files": 0,
        "processed_files": 0,
        "failed_files": [],
        "total_paragraphs": 0,
        "total_characters": 0
    }
    for meta_file in meta_dir.glob("*_metadata.json"):
        report["total_files"] += 1
        try:
            with open(meta_file, encoding="utf-8") as f:
                meta = json.load(f)
            report["processed_files"] += 1
            report["total_paragraphs"] += meta.get("paragraph_count", 0)
            report["total_characters"] += meta.get("character_count", 0)
        except Exception as e:
            logging.warning(f"Summary read error: {meta_file.name} - {e}")
            report["failed_files"].append(meta_file.name)
    report_path = output_dir / "summary_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    logging.info(f"Summary report saved: {report_path}")
    return report
