## 1. Image Preprocessing and OCR Preparation (Last updated: 2026-02-06)
Note: Verify checklist status against docs/DEV_NOTES.md (source of current run results).
Verified today (2026-02-06): photo cataloging, preprocessing, OCR to CSV, pipeline rerun after refactors (see docs/DEV_NOTES.md).
- [x] Implement grayscale, denoising, binarization, and sharpening steps
- [x] Resize images to meet Azure OCR maximum dimension requirements
- [x] Ensure image compression and size limits (4MB) compliance
- [x] Validate preprocessing with batch image processing pipeline
- [x] Integrate photo cataloging as an early pipeline step
- [x] Refactor pipeline controller for modular stage execution
- [x] Add stepwise pipeline execution option with CLI flag
- [x] Test and optimize OCR and parsing pipeline stages
- [x] Integrate improved preprocessing as the default method used in the main batch resizing pipeline (`ImageProcessor.preprocess_image_for_ocr`)
  - Default is smooth (CLAHE + bilateral + sharpen)
  - Binary OCR mode (adaptive threshold + morph close) is optional
## 2. OCR Extraction and Parsing
- [x] Integrate Azure Computer Vision OCR API for raw text extraction using extended OCRService
- [x] Develop and validate OCR extraction test script (`src/tests/test_azure_ocr_service.py`) saving output and char counts
- [x] Develop and run isolated OCR test script targeting new folder `inbox_photos_processed` with absolute path
- [x] Increase retry delay to mitigate 429 Too Many Requests errors
- [x] Export OCR results to CSV for review and downstream processing
- [x] Integrate OpenAI API to parse Azure OCR output into structured metadata
- [x] Develop seamless pipeline integration between Azure OCR and OpenAI parsing
- [ ] Implement error handling and data validation between OCR and parsing steps

## 2b. Normalization and Reconciliation (Pre-enrichment)
- [x] Preserve raw OCR fields and generate normalized fields
- [x] Generate review suggestions for likely catalog-number OCR conflicts (near-row and fuzzy matches)

## 3. Metadata Enrichment and Cataloging
- [ ] Query Discogs and MusicBrainz APIs for metadata enrichment
- [ ] Develop consistency checks and validation logic
- [ ] Implement metadata catalog storage and search functionality

## 4. Pipeline Integration and Automation
- [ ] Develop modular pipeline components for each processing stage
- [ ] Implement end-to-end pipeline runs with logging
- [ ] Add testing for pipeline integration

## 5. Testing and QA
- [x] Unit tests for individual modules
- [ ] Integration tests for OCR and enrichment components
- [x] Perform isolated folder OCR testing to validate rate limiting and retry logic
- [ ] Performance evaluation on large datasets with batching and throttling

## 6. Documentation and Maintenance
- [x] Maintain up-to-date architecture and workflow documentation
- [ ] Document environment setup and configuration
- [ ] Plan for incremental improvements and bug fixes
