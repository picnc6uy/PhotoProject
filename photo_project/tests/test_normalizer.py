import sys
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = WORKSPACE_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from record_catalog.normalizer import MetadataNormalizer


class TestNormalizer:
    @pytest.fixture
    def normalizer(self):
        return MetadataNormalizer()

    def test_normalize_catalog_strips_whitespace_and_dashes(self, normalizer):
        """Test that whitespace and dashes are properly removed from catalog numbers."""
        input_val = "K 12 345 -A"
        result = normalizer._normalize_catalog_number(input_val)
        assert result == "K12345A", f"Expected 'K12345A', got '{result}'"

    def test_normalize_catalog_with_mixed_separators(self, normalizer):
        """Test that various separators (dots, slashes) are removed."""
        input_val = "DGG.413 / 122-2"
        result = normalizer._normalize_catalog_number(input_val)
        assert result == "DG64131222", f"Expected 'DG64131222', got '{result}'"
