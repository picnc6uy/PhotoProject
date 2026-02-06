import csv
import re
import time
from difflib import SequenceMatcher
from pathlib import Path

import requests


def _normalize_text(value: str) -> str:
    if not value:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _similar(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _get_field(row: dict, normalized_key: str, raw_key: str) -> str:
    return row.get(normalized_key) or row.get(raw_key) or ""


def _discogs_search(token: str, user_agent: str, label: str, catno: str, artist: str, title: str):
    url = "https://api.discogs.com/database/search"
    headers = {"User-Agent": user_agent}
    results = []
    search_variants = [
        {"catno": catno, "label": label, "artist": artist, "title": title},
        {"catno": catno, "label": label},
        {"catno": catno},
    ]
    for variant in search_variants:
        params = {
            "per_page": 5,
            "page": 1,
            **{k: v for k, v in variant.items() if v},
        }
        if token:
            params["token"] = token
        for search_type in ("release", "master"):
            params["type"] = search_type
            for attempt in range(3):
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    delay = int(retry_after) if retry_after and retry_after.isdigit() else 2 * (attempt + 1)
                    time.sleep(delay)
                    continue
                data = response.json() if response.content else {}
                results.extend(data.get("results", []))
                break
            else:
                return {"rate_limited": True, "results": []}
            time.sleep(0.7)
    return {"rate_limited": False, "results": results}


def _split_discogs_title(value: str) -> tuple[str, str]:
    if not value:
        return "", ""
    parts = value.split(" - ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", value


def build_enrichment_candidates(
    parsed_csv_path: str,
    suggestions_csv_path: str,
    output_csv_path: str,
    discogs_token: str = "",
    user_agent: str = "RecordCatalogApp/1.0",
):
    parsed_path = Path(parsed_csv_path)
    suggestions_path = Path(suggestions_csv_path)
    output_path = Path(output_csv_path)

    if not parsed_path.exists():
        raise FileNotFoundError(f"Parsed CSV not found: {parsed_path}")
    if not suggestions_path.exists():
        raise FileNotFoundError(f"Suggestions CSV not found: {suggestions_path}")

    with parsed_path.open("r", encoding="utf-8") as csvfile:
        parsed_rows = list(csv.DictReader(csvfile))

    suggestions = {}
    with suggestions_path.open("r", encoding="utf-8") as csvfile:
        for row in csv.DictReader(csvfile):
            fa = row.get("filename_a") or ""
            fb = row.get("filename_b") or ""
            ca = row.get("catalog_a") or ""
            cb = row.get("catalog_b") or ""
            if fa and cb:
                suggestions.setdefault(fa, set()).add(cb)
            if fb and ca:
                suggestions.setdefault(fb, set()).add(ca)

    rows_out = []
    filename_to_index = {}
    for idx, row in enumerate(parsed_rows):
        filename_to_index[row.get("filename") or ""] = idx

    for row in parsed_rows:
        filename = row.get("filename") or ""
        base_cat = _get_field(row, "Catalog Number Normalized", "Catalog Number")
        label = _get_field(row, "Label Normalized", "Label")
        artist = _get_field(row, "Artist Normalized", "Artist")
        title = _get_field(row, "Title Normalized", "Title")

        candidates = {base_cat} if base_cat else set()
        candidates.update(suggestions.get(filename, set()))
        candidates = {c for c in candidates if c}
        if not candidates:
            continue

        scored = []
        row_index = filename_to_index.get(filename, -1)
        neighbor_rows = []
        if row_index >= 0:
            if row_index - 1 >= 0:
                neighbor_rows.append(parsed_rows[row_index - 1])
            if row_index + 1 < len(parsed_rows):
                neighbor_rows.append(parsed_rows[row_index + 1])

        def has_shared_context() -> bool:
            for neighbor in neighbor_rows:
                n_title = _normalize_text(_get_field(neighbor, "Title Normalized", "Title"))
                n_label = _normalize_text(_get_field(neighbor, "Label Normalized", "Label"))
                if _similar(_normalize_text(title), n_title) >= 0.7 and _similar(_normalize_text(label), n_label) >= 0.7:
                    return True
            return False

        shared_context = has_shared_context()

        for catno in sorted(candidates):
            result = _discogs_search(
                discogs_token,
                user_agent,
                label,
                catno,
                artist,
                title,
            )
            if result.get("rate_limited"):
                rows_out.append({
                    "filename": filename,
                    "candidate_catalog": catno,
                    "score": "",
                    "decision": "rate_limited",
                    "discogs_title": "",
                    "discogs_label": "",
                    "discogs_catno": "",
                    "discogs_year": "",
                })
                continue

            best = None
            best_score = 0.0
            for item in result.get("results", []):
                raw_title = item.get("title", "")
                parsed_artist, parsed_title = _split_discogs_title(raw_title)
                d_title = _normalize_text(parsed_title or raw_title)
                d_artist = _normalize_text(parsed_artist or item.get("artist", ""))
                d_label = _normalize_text(" ".join(item.get("label", [])) if isinstance(item.get("label"), list) else item.get("label", ""))
                d_catno = _normalize_text(item.get("catno", ""))

                title_score = _similar(_normalize_text(title), d_title)
                label_score = _similar(_normalize_text(label), d_label)
                artist_score = _similar(_normalize_text(artist), d_artist)
                catno_score = 1.0 if _normalize_text(catno) == d_catno else _similar(_normalize_text(catno), d_catno)

                score = (0.4 * label_score) + (0.3 * title_score) + (0.2 * artist_score) + (0.1 * catno_score)
                # Penalize obvious mismatches when OCR has data but Discogs doesn't align.
                if artist and title and label and artist_score < 0.2 and title_score < 0.2 and label_score < 0.2:
                    score = max(0.0, score - 0.2)
                if label and label_score < 0.2:
                    score = max(0.0, score - 0.1)
                # Boost if neighboring image shares context and Discogs aligns well.
                if shared_context and title_score >= 0.5 and label_score >= 0.5:
                    score = min(1.0, score + 0.05)
                if score > best_score:
                    best_score = score
                    best = item

            scored.append({
                "filename": filename,
                "candidate_catalog": catno,
                "score": round(best_score, 3) if best_score else 0,
                "discogs_title": (best or {}).get("title", ""),
                "discogs_label": (best or {}).get("label", ""),
                "discogs_catno": (best or {}).get("catno", ""),
                "discogs_year": (best or {}).get("year", ""),
            })

        scored.sort(key=lambda r: r["score"], reverse=True)
        top = scored[0] if scored else None
        runner_up = scored[1] if len(scored) > 1 else None
        for i, entry in enumerate(scored):
            if top and entry is top:
                entry["best_for_filename"] = "yes"
                margin = top["score"] - (runner_up["score"] if runner_up else 0)
                if top["score"] >= 0.65 and margin >= 0.1:
                    confidence = "high"
                elif top["score"] >= 0.45:
                    confidence = "medium"
                else:
                    confidence = "low"
                entry["decision"] = f"best_guess_{confidence}"
                entry["score_margin"] = round(margin, 3)
            else:
                entry["best_for_filename"] = ""
                entry["decision"] = "candidate"
                entry["score_margin"] = ""
            entry["rank"] = i + 1
            rows_out.append(entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "filename",
        "candidate_catalog",
        "score",
        "score_margin",
        "rank",
        "best_for_filename",
        "decision",
        "discogs_title",
        "discogs_label",
        "discogs_catno",
        "discogs_year",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    return len(rows_out)
