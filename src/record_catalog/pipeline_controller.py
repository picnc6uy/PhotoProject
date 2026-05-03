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
from .normalizer import MetadataNormalizer
from .reconcile import build_review_suggestions
from .candidate_ranker import build_enrichment_candidates
from .resolved_builder import build_resolved_enriched
from .final_exporter import build_final_archival_catalog, build_final_total_catalog, write_catalog_validation_report

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
        self.normalizer = MetadataNormalizer()

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
                ocr_rows.append({"filename": filename, "ocr_text": text})
                time.sleep(delay_seconds)

        self._save_ocr_csv(ocr_rows)

        return ocr_rows

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

    def run_parsing(self, ocr_rows: list[dict]):
        """Parses OCR texts to extract metadata and writes parsed CSV."""
        print("Starting OCR text parsing...")
        parsed_metadatas = []
        for row in ocr_rows:
            text = row.get("ocr_text", "")
            if not text:
                continue
            parsed = self.parser.parse_text(text)
            if not parsed:
                continue
            parsed["filename"] = row.get("filename")
            parsed_metadatas.append(parsed)
        normalized_metadatas = [self.normalizer.normalize(m) for m in parsed_metadatas]
        self._save_parsed_csv(normalized_metadatas)
        return normalized_metadatas

    def _save_parsed_csv(self, parsed_rows: list[dict]):
        parsed_csv_path = self.config.get("PARSED_METADATA_CSV", "dev_data/record_catalog/data/parsed_metadata.csv")
        if not parsed_rows:
            return
        fieldnames = set()
        for row in parsed_rows:
            fieldnames.update(row.keys())
        fieldnames = sorted(fieldnames)
        with open(parsed_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in parsed_rows:
                writer.writerow(row)
        print(f"Parsed metadata saved to {parsed_csv_path}")

    def run_reconciliation_and_resolve(self):
        parsed_csv_path = self.config.get("PARSED_METADATA_CSV", "dev_data/record_catalog/data/parsed_metadata.csv")
        review_csv_path = self.config.get("REVIEW_SUGGESTIONS_CSV", "dev_data/record_catalog/data/outputs/catalog_review_suggestions.csv")
        candidates_csv_path = self.config.get("ENRICHMENT_CANDIDATES_CSV", "dev_data/record_catalog/data/outputs/enrichment_candidates.csv")
        resolved_csv_path = self.config.get("ENRICHED_RESOLVED_CSV", "dev_data/record_catalog/data/outputs/enriched_resolved.csv")
        final_csv_path = self.config.get("FINAL_ARCHIVAL_CSV", "dev_data/record_catalog/data/outputs/final_archival_catalog.csv")
        consolidated_csv_path = self.config.get("FINAL_ARCHIVAL_CONSOLIDATED_CSV", "dev_data/record_catalog/data/outputs/final_archival_catalog_consolidated.csv")
        total_csv_path = self.config.get("FINAL_TOTAL_CATALOG_CSV", "dev_data/record_catalog/data/outputs/final_total_catalog.csv")
        validation_csv_path = self.config.get("CATALOG_VALIDATION_REPORT_CSV", "dev_data/record_catalog/data/outputs/catalog_validation_report.csv")

        build_review_suggestions(parsed_csv_path, review_csv_path)
        build_enrichment_candidates(
            parsed_csv_path,
            review_csv_path,
            candidates_csv_path,
            discogs_token=self.config.get("DISCOGS_TOKEN", ""),
            user_agent=self.config.get("MUSICBRAINZ_USER_AGENT", "RecordCatalogApp/1.0"),
        )
        build_resolved_enriched(
            parsed_csv_path,
            candidates_csv_path,
            resolved_csv_path,
            self.config.config_path,
        )
        build_final_archival_catalog(resolved_csv_path, final_csv_path, consolidate=False)
        build_final_archival_catalog(resolved_csv_path, consolidated_csv_path, consolidate=True)
        build_final_total_catalog(resolved_csv_path, total_csv_path)
        write_catalog_validation_report(consolidated_csv_path, validation_csv_path)

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

        ocr_rows = self.run_ocr(ocr_folder)

        self.run_parsing(ocr_rows)

        self.run_reconciliation_and_resolve()

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
        ocr_rows = self.run_ocr(ocr_folder)

        input("Press Enter to run OCR text parsing...")
        self.run_parsing(ocr_rows)

        input("Press Enter to run reconciliation and resolved enrichment...")
        self.run_reconciliation_and_resolve()
