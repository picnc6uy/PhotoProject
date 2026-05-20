import re


class MetadataNormalizer:
    """Normalize parsed metadata fields while preserving raw values."""

    _whitespace_re = re.compile(r"\s+")

    def normalize(self, metadata: dict) -> dict:
        if not metadata:
            return {}

        normalized = metadata.copy()

        for field in ("Label", "Artist", "Title", "Catalog Number"):
            if field in metadata:
                raw_value = metadata.get(field)
                normalized[f"{field} Raw"] = raw_value
                normalized_value = self._normalize_text(raw_value, field == "Label")
                if field == "Catalog Number":
                    normalized_value = self._normalize_catalog_number(normalized_value)
                normalized[f"{field} Normalized"] = normalized_value
                # Use normalized value for downstream enrichment while preserving raw
                normalized[field] = normalized_value

        return normalized

    def _normalize_text(self, value, upper: bool = False):
        if value is None:
            return None
        text = str(value).strip()
        text = self._whitespace_re.sub(" ", text)
        return text.upper() if upper else text

    def _normalize_catalog_number(self, value):
        if value is None:
            return None
        text = str(value).strip().upper()
        # Remove common separators and whitespace
        text = re.sub(r"[\s\-_/.]+", "", text)

        # Replace common OCR confusions when adjacent to digits
        def replace_confusable(ch, prev_is_digit, next_is_digit):
            if ch == "O" and (prev_is_digit or next_is_digit):
                return "0"
            if ch == "I" and (prev_is_digit or next_is_digit):
                return "1"
            if ch == "S" and (prev_is_digit or next_is_digit):
                return "5"
            if ch == "B" and (prev_is_digit or next_is_digit):
                return "8"
            if ch == "Z" and (prev_is_digit or next_is_digit):
                return "2"
            if ch == "G" and (prev_is_digit or next_is_digit):
                return "6"
            return ch

        chars = list(text)
        for i, ch in enumerate(chars):
            prev_is_digit = i > 0 and chars[i - 1].isdigit()
            next_is_digit = i < len(chars) - 1 and chars[i + 1].isdigit()
            chars[i] = replace_confusable(ch, prev_is_digit, next_is_digit)
        return "".join(chars)
