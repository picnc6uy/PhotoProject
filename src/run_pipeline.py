import os
import sys
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


def main():
    parser = argparse.ArgumentParser(description="Run the record catalog pipeline")
    parser.add_argument(
        "--stepwise", action="store_true", help="Run pipeline step-by-step with pauses"
    )
    args = parser.parse_args()

    print("Loading configuration...")
    config = ConfigManager(CONFIG_PATH)

    pipeline = PipelineController(config)

    if args.stepwise:
        print("Running pipeline in stepwise mode...")
        pipeline.run_stepwise()
    else:
        print("Running full catalog pipeline...")
        pipeline.run()

    print("Pipeline finished.")


if __name__ == "__main__":
    main()
