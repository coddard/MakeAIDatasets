import argparse
from src.main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MakeAIDatasets CLI")
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--process", action="store_true", help="Process all input files")
    action_group.add_argument("--build-dataset", action="store_true", help="Build Hugging Face dataset")
    action_group.add_argument("--upload-hf", action="store_true", help="Upload dataset to Hugging Face Hub")

    filter_group = parser.add_argument_group("Filtering options")
    filter_group.add_argument("--lang", type=str, default="en", help="Language code to filter (default: en)")
    filter_group.add_argument("--output-format", type=str, choices=["txt", "json", "csv"], default="txt", help="Output format")

    args = parser.parse_args()
    main(args)
