import csv
import re
from difflib import SequenceMatcher
from collections import defaultdict


CONFUSION_MAP = {
    "3": "8",
    "8": "3",
    "5": "S",
    "S": "5",
    "0": "O",
    "O": "0",
    "1": "I",
    "I": "1",
}


def _normalize_key(value: str) -> str:
    if not value:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _confusable(a: str, b: str) -> bool:
    if not a or not b:
        return False
    if len(a) != len(b):
        return False
    diffs = 0
    for ca, cb in zip(a, b):
        if ca == cb:
            continue
        diffs += 1
        if CONFUSION_MAP.get(ca) != cb:
            return False
    return diffs == 1


def _get_catalog(row: dict) -> str:
    return row.get("Catalog Number Normalized") or row.get("Catalog Number") or ""


def _get_artist(row: dict) -> str:
    return row.get("Artist Normalized") or row.get("Artist") or ""


def _get_title(row: dict) -> str:
    return row.get("Title Normalized") or row.get("Title") or ""


def build_review_suggestions(parsed_csv_path: str, output_csv_path: str):
    with open(parsed_csv_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Group by normalized (Artist, Title) when present
    groups = defaultdict(list)
    for row in rows:
        artist = _normalize_key(_get_artist(row))
        title = _normalize_key(_get_title(row))
        key = (artist, title)
        groups[key].append(row)

    suggestions = []

    # 1) Conflicts within same artist/title
    for (artist, title), items in groups.items():
        if not artist and not title:
            continue
        cats = [_get_catalog(i) for i in items]
        cats = [c for c in cats if c]
        if len(set(cats)) <= 1:
            continue

        # Compare every pair for close/confusable catalog numbers
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a = _get_catalog(items[i])
                b = _get_catalog(items[j])
                if not a or not b:
                    continue
                if _confusable(a, b) or _similar(a, b) >= 0.9:
                    suggestions.append({
                        "issue_type": "catalog_conflict_same_title",
                        "artist": items[i].get("Artist"),
                        "title": items[i].get("Title"),
                        "filename_a": items[i].get("filename"),
                        "catalog_a": a,
                        "filename_b": items[j].get("filename"),
                        "catalog_b": b,
                        "note": "Same artist/title with close catalog numbers (possible OCR confusion).",
                    })

    # 1b) Fuzzy match artist/title, then check for confusable catalog numbers.
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            artist_a = _normalize_key(_get_artist(rows[i]))
            artist_b = _normalize_key(_get_artist(rows[j]))
            title_a = _normalize_key(_get_title(rows[i]))
            title_b = _normalize_key(_get_title(rows[j]))

            if not artist_a and not title_a:
                continue
            if not artist_b and not title_b:
                continue

            artist_sim = _similar(artist_a, artist_b) if artist_a and artist_b else 0
            title_sim = _similar(title_a, title_b) if title_a and title_b else 0
            if artist_sim < 0.85 and title_sim < 0.85:
                continue

            a = _get_catalog(rows[i])
            b = _get_catalog(rows[j])
            if not a or not b:
                continue
            if _confusable(a, b) or _similar(a, b) >= 0.9:
                suggestions.append({
                    "issue_type": "catalog_conflict_fuzzy_match",
                    "artist": rows[i].get("Artist"),
                    "title": rows[i].get("Title"),
                    "filename_a": rows[i].get("filename"),
                    "catalog_a": a,
                    "filename_b": rows[j].get("filename"),
                    "catalog_b": b,
                    "note": "Fuzzy artist/title match with close catalog numbers (possible OCR confusion).",
                })

    # 2) Same catalog number but different titles (possible front/back)
    cat_groups = defaultdict(list)
    for row in rows:
        cat = _get_catalog(row)
        if cat:
            cat_groups[cat].append(row)

    for cat, items in cat_groups.items():
        titles = set(_normalize_key(_get_title(i)) for i in items if _get_title(i))
        if len(titles) <= 1:
            continue
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                ta = _normalize_key(_get_title(items[i]))
                tb = _normalize_key(_get_title(items[j]))
                if ta and tb and ta != tb:
                    suggestions.append({
                        "issue_type": "same_catalog_diff_titles",
                        "artist": items[i].get("Artist"),
                        "title": f"{items[i].get('Title')} | {items[j].get('Title')}",
                        "filename_a": items[i].get("filename"),
                        "catalog_a": cat,
                        "filename_b": items[j].get("filename"),
                        "catalog_b": cat,
                        "note": "Same catalog number with different titles (possible front/back).",
                    })

    # 3) Neighbor-row comparison for likely front/back adjacency
    for idx, row in enumerate(rows):
        for offset in (-1, 1):
            j = idx + offset
            if j < 0 or j >= len(rows):
                continue
            a = _get_catalog(row)
            b = _get_catalog(rows[j])
            if not a or not b:
                continue
            if _confusable(a, b) or _similar(a, b) >= 0.9:
                suggestions.append({
                    "issue_type": "catalog_conflict_neighbor_rows",
                    "artist": row.get("Artist"),
                    "title": row.get("Title"),
                    "filename_a": row.get("filename"),
                    "catalog_a": a,
                    "filename_b": rows[j].get("filename"),
                    "catalog_b": b,
                    "note": "Neighboring rows with close catalog numbers (possible front/back pair).",
                })

    if not suggestions:
        return 0

    fieldnames = [
        "issue_type",
        "artist",
        "title",
        "filename_a",
        "catalog_a",
        "filename_b",
        "catalog_b",
        "note",
    ]
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in suggestions:
            writer.writerow(row)

    return len(suggestions)
