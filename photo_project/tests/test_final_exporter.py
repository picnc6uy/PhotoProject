import sys
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = WORKSPACE_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from record_catalog.final_exporter import _base_catalog_number


class TestFinalExporter:
    def test_base_catalog_strips_side_suffix(self):
        """Test that side suffixes (A/B) with preceding dash or space are stripped."""
        input_val = "K 12 345 -A"
        result = _base_catalog_number(input_val)
        assert result == "K 12 345", f"Expected 'K 12 345', got '{result}'"

    def test_base_catalog_no_suffix_to_strip(self):
        """Test catalog without side suffix is returned unchanged."""
        input_val = "DGG.413 / 122-2"
        result = _base_catalog_number(input_val)
        assert result == "DGG.413 / 122-2", f"Expected 'DGG.413 / 122-2', got '{result}'"
