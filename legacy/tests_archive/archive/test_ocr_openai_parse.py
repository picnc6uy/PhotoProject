import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from record_catalog.config_manager import ConfigManager
from record_catalog.parser import OCRParser

# Updated example OCR text with extra metadata fields for testing
TEST_OCR_TEXT = """RCA Victor LSP-121 Beethoven - The Nine Symphonies Bruno Walter Columbia Masterworks 8 LP Remastered Limited Edition Release Date: 2020-10-15 Barcode: 1234567890123 Audio Format: Stereo High"""


def test_openai_ocr_parse():
    config = ConfigManager()
    parser = OCRParser(config)

    if not config.get("OPENAI_API_KEY"):
        print("OpenAI API key not set in environment or config. Test aborted.")
        return

    print("Sending OCR text to OpenAI for parsing...")
    parsed = parser.parse_text(TEST_OCR_TEXT)
    print("Parsed Metadata:")
    print(parsed)


if __name__ == "__main__":
    test_openai_ocr_parse()
