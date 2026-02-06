import csv
from dataclasses import dataclass

@dataclass
class CatalogEntry:
    item_number: int
    composer: str
    title: str
    performer: str
    label: str
    catalog_number: str
    format_disc_count: str
    confidence: str
    notes: str


class CatalogManager:
    """Manages the catalog data storage and output."""

    def __init__(self, config):
        self.config = config
        self.entries = []  # type: list[CatalogEntry]

    def add_entry(self, entry: CatalogEntry):
        self.entries.append(entry)

    def load_from_csv(self, csv_path: str):
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.entries = []
            for row in reader:
                entry = CatalogEntry(
                    item_number=int(row.get('Item #', 0)),
                    composer=row.get('Composer / Primary', ''),
                    title=row.get('Title', ''),
                    performer=row.get('Performer / Ensemble / Conductor', ''),
                    label=row.get('Label', ''),
                    catalog_number=row.get('Catalog Number', ''),
                    format_disc_count=row.get('Format / Disc Count', ''),
                    confidence=row.get('Confidence', ''),
                    notes=row.get('Notes', ''),
                )
                self.entries.append(entry)

    def save_to_csv(self, csv_path: str):
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Item #', 'Composer / Primary', 'Title', 'Performer / Ensemble / Conductor', 
                          'Label', 'Catalog Number', 'Format / Disc Count', 'Confidence', 'Notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.entries:
                writer.writerow({
                    'Item #': entry.item_number,
                    'Composer / Primary': entry.composer,
                    'Title': entry.title,
                    'Performer / Ensemble / Conductor': entry.performer,
                    'Label': entry.label,
                    'Catalog Number': entry.catalog_number,
                    'Format / Disc Count': entry.format_disc_count,
                    'Confidence': entry.confidence,
                    'Notes': entry.notes,
                })

    def find_entry(self, item_number: int):
        for entry in self.entries:
            if entry.item_number == item_number:
                return entry
        return None
