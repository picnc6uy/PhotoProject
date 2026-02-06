import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from record_catalog.config_manager import ConfigManager
from record_catalog.enricher import MetadataEnricher

# Sample parsed metadata with minimal fields
SAMPLE_METADATA = {
    "Title": "Symphony No. 9",
    "Artist": "Ludwig van Beethoven",
    "Label": "Deutsche Grammophon",
    "Catalog Number": "12345",
    "Year": "1824",
}

def test_enrich_metadata():
    config = ConfigManager()
    enricher = MetadataEnricher(config)
    enriched = enricher.enrich_metadata(SAMPLE_METADATA)
    print("Enriched Metadata:")
    print(enriched)

if __name__ == '__main__':
    test_enrich_metadata()
