import argparse
from src.main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MakeAIDatasets CLI")
    parser.add_argument("--process", action="store_true", help="Process all input files")
    parser.add_argument("--build-dataset", action="store_true", help="Build Hugging Face dataset")
    parser.add_argument("--upload-hf", action="store_true", help="Upload dataset to Hugging Face Hub")
    parser.add_argument("--lang", type=str, default="en", help="Language code to filter (default: en)")
    parser.add_argument("--output-format", type=str, choices=["txt", "json", "csv"], default="txt", help="Output format")
    args = parser.parse_args()
    main(args)
