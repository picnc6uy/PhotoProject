import json
import openai
from record_catalog.config_manager import ConfigManager

class OCRParser:
    """Parses raw OCR text data into structured metadata format using OpenAI GPT."""

    def __init__(self, config):
        self.config = config
        self.api_key = config.get("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def _openai_parse_prompt(self, ocr_text: str) -> str:
        prompt = f"""Extract the following info from the record label OCR text below.

Fields to extract: Title, Artist, Label, Catalog Number, Format, Year, Notes.

OCR Text:
{ocr_text}

Provide JSON output with these fields. If a field cannot be found, set it to null."""
        return prompt

    def parse_text(self, ocr_text: str) -> dict:
        if not self.api_key:
            print("OpenAI API key not set. Parsing aborted.")
            return {}

        prompt = self._openai_parse_prompt(ocr_text)
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.0,
            )
            print(f"OpenAI response object: {response}")
            content = response.choices[0].message.content
            print(f"OpenAI raw response content:\n{content}")

            # Strip markdown json fences if present
            if content.startswith("```json") and content.endswith("```"):
                content = content[len("```json"): -3].strip()

            parsed = json.loads(content)
            return parsed
        except Exception as e:
            print(f"OpenAI parsing error: {e}")
            return {}

    def batch_parse(self, ocr_texts: list[str]) -> list[dict]:
        results = []
        for text in ocr_texts:
            parsed = self.parse_text(text)
            results.append(parsed)
        return results
