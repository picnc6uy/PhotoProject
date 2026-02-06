import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from record_catalog.config_manager import ConfigManager
from record_catalog.enricher import MetadataEnricher

def test_discogs_enricher():
    config = ConfigManager()
    enricher = MetadataEnricher(config)
    if not config.get("DISCOGS_TOKEN"):
        print("Discogs token not set in environment or config. Test aborted.")
        return

    # Sample minimal metadata for query
    sample_metadata = {"Label": "RCA", "Catalog Number": "LSP-121"}
    try:
        enriched = enricher.enrich_metadata(sample_metadata)
        if enriched:
            print(f"Discogs Enricher Test Passed: Received enriched data keys: {list(enriched.keys())}")
        else:
            print("Discogs Enricher Test Failed: No data returned.")
    except Exception as e:
        print("Discogs Enricher Test Exception:", e)

if __name__ == "__main__":
    test_discogs_enricher()
