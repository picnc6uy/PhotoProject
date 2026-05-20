import csv
import codecs
import re
from pathlib import Path


def _clean(value: str) -> str:
    text = (value or "").strip()
    try:
        text = codecs.decode(text.encode("latin-1"), "utf-8")
    except Exception:
        pass
    text = " ".join(text.split())
    text = text.strip(" ,;")
    return text


def _title_case_label(value: str) -> str:
    if not value:
        return value
    return " ".join(word.capitalize() for word in value.split())


def _non_zero_row(row: dict) -> bool:
    return any(_clean(row.get(k, "")) for k in ("Artist", "Title", "Catalog Number", "Catalog Number Resolved"))


def _dedupe_key(row: dict) -> tuple:
    cat = _clean(row.get("Catalog Number Resolved") or row.get("Catalog Number"))
    artist = _clean(row.get("Artist"))
    title = _clean(row.get("Title"))
    if cat:
        return ("catalog", cat.lower())
    return ("artist_title", artist.lower(), title.lower())


def _merge_rows(rows: list[dict]) -> dict:
    base = dict(rows[0])
    filenames = []
    for row in rows:
        fname = _clean(row.get("filename"))
        if fname:
            filenames.append(fname)
        for key in ("Artist", "Title", "Label", "Catalog Number Resolved", "Catalog Number"):
            if not _clean(base.get(key)):
                base[key] = row.get(key)
        for key in ("Format", "Disc Count"):
            if not _clean(base.get(key)):
                base[key] = row.get(key)
    base["__filenames"] = sorted(set(filenames))
    return base


def _normalize_catalog_number(label: str, catalog: str) -> str:
    if not catalog:
        return catalog
    if label.lower() == "decca" and catalog.isdigit():
        return f"K{catalog}"
    return catalog


def _extract_side_suffix(catalog: str) -> str:
    if not catalog:
        return ""
    match = re.search(r"(?:^|[-\s])([AB])$", catalog.strip(), re.IGNORECASE)
    return match.group(1).upper() if match else ""


def _base_catalog_number(catalog: str) -> str:
    if not catalog:
        return catalog
    return re.sub(r"[-\s]([AB])$", "", catalog.strip(), flags=re.IGNORECASE).strip()


def build_final_archival_catalog(input_csv: str, output_csv: str, consolidate: bool = True):
    input_path = Path(input_csv)
    output_path = Path(output_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    with input_path.open("r", encoding="utf-8") as csvfile:
        rows = [r for r in csv.DictReader(csvfile) if _non_zero_row(r)]

    if consolidate:
        grouped = {}
        for row in rows:
            key = _dedupe_key(row)
            grouped.setdefault(key, []).append(row)
        merged = []
        for _, group in grouped.items():
            merged.append(_merge_rows(group))
    else:
        merged = [_merge_rows([row]) for row in rows]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "File name",
        "Composer / Primary",
        "Title/",
        "Performer_Ensemble_Conductor",
        "Label",
        "Catalog Number",
        "Format",
        "Disc Count",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in merged:
            out = {
                "File name": ", ".join(row.get("__filenames", [])),
                "Composer / Primary": _clean(row.get("Artist")),
                "Title/": _clean(row.get("Title")),
                "Performer_Ensemble_Conductor": _clean(row.get("Artist")),
                "Label": _title_case_label(_clean(row.get("Label"))),
                "Catalog Number": _normalize_catalog_number(
                    _clean(row.get("Label")),
                    _clean(row.get("Catalog Number Resolved") or row.get("Catalog Number")),
                ),
                "Format": _clean(row.get("Format")),
                "Disc Count": _clean(row.get("Disc Count")),
            }
            writer.writerow(out)


def build_final_total_catalog(input_csv: str, output_csv: str):
    input_path = Path(input_csv)
    output_path = Path(output_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    with input_path.open("r", encoding="utf-8") as csvfile:
        rows = [r for r in csv.DictReader(csvfile) if _non_zero_row(r)]

    grouped = {}
    for row in rows:
        catalog = _clean(row.get("Catalog Number Resolved") or row.get("Catalog Number"))
        base = _base_catalog_number(catalog)
        key = ("catalog", base.lower()) if base else _dedupe_key(row)
        grouped.setdefault(key, []).append(row)

    merged = []
    for _, group in grouped.items():
        merged.append(_merge_rows(group))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "File name",
        "Side A Files",
        "Side B Files",
        "Composer / Primary",
        "Title/",
        "Performer_Ensemble_Conductor",
        "Label",
        "Catalog Number",
        "Format",
        "Disc Count",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in merged:
            filenames = row.get("__filenames", [])
            side_a = []
            side_b = []
            for original in rows:
                if _clean(original.get("filename")) not in filenames:
                    continue
                catalog = _clean(original.get("Catalog Number Resolved") or original.get("Catalog Number"))
                side = _extract_side_suffix(catalog)
                if side == "A":
                    side_a.append(_clean(original.get("filename")))
                elif side == "B":
                    side_b.append(_clean(original.get("filename")))
            out = {
                "File name": ", ".join(filenames),
                "Side A Files": ", ".join(sorted(set(side_a))),
                "Side B Files": ", ".join(sorted(set(side_b))),
                "Composer / Primary": _clean(row.get("Artist")),
                "Title/": _clean(row.get("Title")),
                "Performer_Ensemble_Conductor": _clean(row.get("Artist")),
                "Label": _title_case_label(_clean(row.get("Label"))),
                "Catalog Number": _normalize_catalog_number(
                    _clean(row.get("Label")),
                    _base_catalog_number(_clean(row.get("Catalog Number Resolved") or row.get("Catalog Number"))),
                ),
                "Format": _clean(row.get("Format")),
                "Disc Count": _clean(row.get("Disc Count")),
            }
            writer.writerow(out)


def _validate_catalog_number(label: str, catalog: str) -> str:
    if not catalog:
        return "missing_catalog"
    if label.lower() == "victor":
        cleaned = catalog.replace(" ", "")
        if cleaned.endswith(("-A", "-B")):
            cleaned = cleaned[:-2]
        if not cleaned.replace("-", "").isdigit():
            return "victor_non_numeric"
        return ""
    if label.lower() == "decca" and not any(catalog.upper().startswith(prefix) for prefix in ("G-", "P-G", "K", "REJ", "KI")):
        return "decca_unexpected_prefix"
    return ""


def write_catalog_validation_report(input_csv: str, output_csv: str):
    input_path = Path(input_csv)
    output_path = Path(output_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    issues = []
    with input_path.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            label = _clean(row.get("Label"))
            catalog = _clean(row.get("Catalog Number"))
            issue = _validate_catalog_number(label, catalog)
            if issue:
                issues.append({
                    "File name": row.get("File name"),
                    "Label": label,
                    "Catalog Number": catalog,
                    "Issue": issue,
                })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["File name", "Label", "Catalog Number", "Issue"])
        writer.writeheader()
        writer.writerows(issues)
