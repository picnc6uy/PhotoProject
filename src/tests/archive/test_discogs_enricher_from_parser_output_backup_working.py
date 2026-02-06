import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from record_catalog.config_manager import ConfigManager
from record_catalog.enricher import MetadataEnricher

# Sample parsed OCR output from the parser
SAMPLE_PARSED_METADATA = {
    "Title": "The Nine Symphonies",
    "Artist": "Bruno Walter",
    "Label": "RCA Victor",
    "Catalog Number": "LSP-121",
    "Format": "8 LP",
    "Year": None,
    "Notes": "High"
}


def test_enrich_from_parser_output():
    config = ConfigManager()
    enricher = MetadataEnricher(config)

    if not config.get("DISCOGS_TOKEN"):
        print("Discogs token not set in environment or config. Test aborted.")
        return

    print("Testing Discogs enrichment with sample OCR parsed metadata...\nBackup working version")
    enriched = enricher.enrich_metadata(SAMPLE_PARSED_METADATA)
    print("Enriched Metadata Result:")
    print(enriched)


if __name__ == "__main__":
    test_enrich_from_parser_output()
