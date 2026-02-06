import os
import time
import csv
from msrestazure.azure_exceptions import CloudError
from .image_processor import ImageProcessor
from .ocr_service import OCRService
from .parser import OCRParser
from .enricher import MetadataEnricher
from .catalog_manager import CatalogManager, CatalogEntry  # Updated import to include CatalogEntry
from .photo_catalog_manager import PhotoCatalogManager  # New import for photo cataloging
from .config_manager import ConfigManager

class PipelineController:
    """Orchestrates the entire cataloging pipeline sequence.

    Note: This pipeline uses the `ImageProcessor.batch_resize_images` method,
    which by default applies the validated modern image preprocessing pipeline
    (grayscale, CLAHE, denoising, adaptive thresholding, morphological closing, sharpening)
    via the `ImageProcessor.preprocess_image_for_ocr` method.
    """

    def __init__(self, config):
        self.config = config
        self.image_processor = None
        self.ocr_service = None
        self.parser = None
        self.enricher = None
        self.catalog_manager = None

    def setup_components(self):
        self.image_processor = ImageProcessor(self.config)
        self.ocr_service = OCRService(self.config)
        self.parser = OCRParser(self.config)
        self.enricher = MetadataEnricher(self.config)
        self.catalog_manager = CatalogManager(self.config)

    def run_photo_catalog(self):
        """Executes the photo cataloging process."""
        photo_dir = self.config.get('SOURCE_PHOTO_FOLDER')
        photo_catalog_csv = self.config.get('PHOTO_CATALOG_OUTPUT_CSV')
        photo_cataloger = PhotoCatalogManager(photo_dir, photo_catalog_csv)
        print(f"Starting photo cataloging of {photo_dir}...")
        photo_cataloger.catalog_photos()
        print(f"Photo catalog CSV saved to {photo_catalog_csv}")

    def run_image_preprocessing(self, source_folder, ocr_folder):
        """Starts batch image resize and processes images for OCR."""
        print("Starting batch image resize...")
        self.image_processor.batch_resize_images(source_folder, ocr_folder)
        print("Image resize complete.")

    def run_ocr(self, ocr_folder):
        """Executes OCR processing on resized images."""
        print("Starting OCR processing...")
        ocr_texts = []
        ocr_rows = []
        delay_seconds = self.config.get("OCR_INTER_IMAGE_DELAY", 7)
        max_retries = self.config.get("MAX_OCR_RETRIES", 3)
        for filename in sorted(os.listdir(ocr_folder)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_path = os.path.join(ocr_folder, filename)
                ocr_result = {}
                attempts = 0
                while attempts <= max_retries:
                    try:
                        ocr_result = self.ocr_service.process_image(image_path)
                        break
                    except CloudError as e:
                        if e.status_code == 429:
                            wait_time = delay_seconds * (2 ** attempts)
                            print(f"429 Too Many Requests for {filename}. Retry {attempts + 1}/{max_retries} after {wait_time} seconds.")
                            time.sleep(wait_time)
                            attempts += 1
                        else:
                            print(f"Azure CloudError for {filename}: {e}")
                            break
                    except Exception as e:
                        print(f"OCR error for {filename}: {e}")
                        break
                text = ocr_result.get('text', '')
                print(f"OCR extracted {len(text)} chars from {filename}")
                ocr_texts.append(text)
                ocr_rows.append({"filename": filename, "ocr_text": text})
                time.sleep(delay_seconds)

        self._save_ocr_csv(ocr_rows)

        return ocr_texts

    def _save_ocr_csv(self, ocr_rows: list[dict]):
        """Write OCR results to CSV for downstream parsing."""
        ocr_csv_path = self.config.get("OCR_PARSED_CSV") or self.config.get("OCR_AZURE_RESULTS_CSV")
        if not ocr_csv_path:
            return
        with open(ocr_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["filename", "ocr_text"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in ocr_rows:
                writer.writerow(row)
        print(f"OCR results saved to {ocr_csv_path}")

    def run_parsing(self, ocr_texts):
        """Parses OCR texts to extract metadata."""
        print("Starting OCR text parsing...")
        parsed_metadatas = self.parser.batch_parse(ocr_texts)
        return parsed_metadatas

    def run_enrichment(self, parsed_metadatas):
        """Enriches parsed metadata."""
        print("Starting metadata enrichment...")
        enriched_metadatas = self.enricher.batch_enrich(parsed_metadatas)
        return enriched_metadatas

    def run_catalog_save(self, enriched_metadatas):
        """Saves enriched metadata to the catalog."""
        print("Updating catalog entries...")
        for metadata in enriched_metadatas:
            entry = CatalogEntry(
                item_number=metadata.get('item_number', 0),
                composer=metadata.get('Artist'),
                title=metadata.get('Title'),
                performer=metadata.get('Artist'),
                label=metadata.get('Label'),
                catalog_number=metadata.get('Catalog Number'),
                format_disc_count=metadata.get('Format'),
                confidence='',
                notes=metadata.get('Notes') or '',
            )
            self.catalog_manager.add_entry(entry)

        catalog_output = self.config.get('CATALOG_OUTPUT_PATH')
        self.catalog_manager.save_to_csv(catalog_output)
        print(f"Catalog saved to {catalog_output}")

    def run(self):
        """Executes the full pipeline."""
        self.setup_components()

        # Run photo cataloging before other steps
        self.run_photo_catalog()

        source_folder = self.config.get('SOURCE_PHOTO_FOLDER')
        ocr_folder = self.config.get('OCR_IMAGE_FOLDER')
        self.run_image_preprocessing(source_folder, ocr_folder)

        ocr_texts = self.run_ocr(ocr_folder)

        parsed_metadatas = self.run_parsing(ocr_texts)

        enriched_metadatas = self.run_enrichment(parsed_metadatas)

        self.run_catalog_save(enriched_metadatas)

    def run_stepwise(self):
        """Run pipeline in steps, prompting between stages."""
        self.setup_components()

        input("Press Enter to run photo cataloging...")
        self.run_photo_catalog()

        source_folder = self.config.get('SOURCE_PHOTO_FOLDER')
        ocr_folder = self.config.get('OCR_IMAGE_FOLDER')
        input("Press Enter to run image preprocessing...")
        self.run_image_preprocessing(source_folder, ocr_folder)

        input("Press Enter to run OCR extraction...")
        ocr_texts = self.run_ocr(ocr_folder)

        input("Press Enter to run OCR text parsing...")
        parsed_metadatas = self.run_parsing(ocr_texts)

        input("Press Enter to run metadata enrichment...")
        enriched_metadatas = self.run_enrichment(parsed_metadatas)

        input("Press Enter to save catalog CSV...")
        self.run_catalog_save(enriched_metadatas)
