import os
import sys
import logging
from datetime import datetime
import argparse  # Added import for argparse

from record_catalog.config_manager import ConfigManager
from record_catalog.pipeline_controller import PipelineController

# Expected config.yaml keys to be set:
# - SOURCE_PHOTO_FOLDER: Folder containing source photos
# - PHOTO_CATALOG_OUTPUT_CSV: Path to save photo catalog CSV
# - DESC_IMAGE_FOLDER: Folder for resized description images
# - OCR_IMAGE_FOLDER: Folder for resized OCR images
# - CATALOG_OUTPUT_PATH: Path to save final catalog CSV

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


class TeeStream:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            try:
                stream.write(data)
            except UnicodeEncodeError:
                encoding = getattr(stream, "encoding", None) or "utf-8"
                safe = data.encode(encoding, "backslashreplace").decode(encoding, "backslashreplace")
                stream.write(safe)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def setup_logging():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_dir = os.path.join(
        project_root, "dev_data", "record_catalog", "data", "outputs", "logs"
    )
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"pipeline_run_{timestamp}.log")

    log_file = open(log_path, "w", encoding="utf-8")
    sys.stdout = TeeStream(sys.stdout, log_file)
    sys.stderr = TeeStream(sys.stderr, log_file)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    print(f"Logging to {log_path}")


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Run the record catalog pipeline")
    parser.add_argument(
        "--stepwise", action="store_true", help="Run pipeline step-by-step with pauses"
    )
    parser.add_argument(
        "--stop-after",
        choices=["photo_catalog", "preprocess", "ocr", "parse", "resolve"],
        help="Stop after the specified stage (non-interactive)",
    )
    args = parser.parse_args()

    print("Loading configuration...")
    config = ConfigManager(CONFIG_PATH)

    pipeline = PipelineController(config)

    if args.stepwise:
        print("Running pipeline in stepwise mode...")
        pipeline.run_stepwise()
    elif args.stop_after:
        print(f"Running pipeline until stage: {args.stop_after}...")
        pipeline.setup_components()

        pipeline.run_photo_catalog()
        if args.stop_after == "photo_catalog":
            print("Stopping after photo cataloging.")
            print("Pipeline finished.")
            return

        source_folder = config.get('SOURCE_PHOTO_FOLDER')
        ocr_folder = config.get('OCR_IMAGE_FOLDER')
        pipeline.run_image_preprocessing(source_folder, ocr_folder)
        if args.stop_after == "preprocess":
            print("Stopping after preprocessing.")
            print("Pipeline finished.")
            return

        ocr_rows = pipeline.run_ocr(ocr_folder)
        if args.stop_after == "ocr":
            print("Stopping after OCR.")
            print("Pipeline finished.")
            return

        pipeline.run_parsing(ocr_rows)
        if args.stop_after == "parse":
            print("Stopping after parsing.")
            print("Pipeline finished.")
            return

        pipeline.run_reconciliation_and_resolve()
        if args.stop_after == "resolve":
            print("Stopping after resolve.")
            print("Pipeline finished.")
            return
        print("Pipeline finished.")
    else:
        print("Running full catalog pipeline...")
        pipeline.run()

    print("Pipeline finished.")


if __name__ == "__main__":
    main()
