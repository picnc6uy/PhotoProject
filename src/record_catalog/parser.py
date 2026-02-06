import json
import openai
from record_catalog.config_manager import ConfigManager

class OCRParser:
    """Parses raw OCR text data into structured metadata format using OpenAI GPT."""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.api_key = config.get("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def _build_parse_prompt(self, ocr_text: str) -> str:
        """Constructs the prompt for extracting critical metadata from the OCR text."""
        prompt = f"""You are an expert music record cataloger.

Extract only the following critical metadata from the OCR text of a record label into a valid JSON object: Label, Artist, Title, Catalog Number.

Set any missing or uncertain fields to null.

Output ONLY valid JSON without any commentary or formatting.
OCR Text:
{ocr_text}"""
        return prompt

    def parse_text(self, ocr_text: str) -> dict:
        if not self.api_key:
            print("OpenAI API key not set. Parsing aborted.")
            return {}

        prompt = self._build_parse_prompt(ocr_text)

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350,
                temperature=0.0,
            )
            print(f"OpenAI response object ID: {response.id}")
            content = response.choices[0].message.content
            print(f"OpenAI raw response content:\n{content}")

            # Strip markdown fences if present
            if content and content.startswith("```json") and content.endswith("```"):
                content = content[len("```json"): -3].strip()

            if not content:
                print("Error: Empty response content from OpenAI")
                return {}

            parsed = json.loads(content)
            print("Parsed metadata:")
            print(parsed)

            # Normalize key naming for downstream pipeline compatibility
            if "CatalogNumber" in parsed and "Catalog Number" not in parsed:
                parsed["Catalog Number"] = parsed.pop("CatalogNumber")

            null_fields = [k for k, v in parsed.items() if v is None]
            if null_fields:
                print(f"Warning: These fields were missing or uncertain and set to null: {null_fields}")

            return parsed
        except Exception as e:
            print(f"OpenAI parsing error: {e}")
            return {}

    def batch_parse(self, ocr_texts: list[str]) -> list[dict]:
        results = []
        for text in ocr_texts:
            results.append(self.parse_text(text))
        return results

# ... existing code ...
