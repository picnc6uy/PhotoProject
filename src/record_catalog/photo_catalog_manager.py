import os
import csv
from datetime import datetime
import logging

class PhotoCatalogManager:
    """Manages photo cataloging by generating CSV with photo metadata."""

    def __init__(self, photo_dir, output_csv):
        self.photo_dir = photo_dir
        self.output_csv = output_csv

    def catalog_photos(self):
        try:
            photo_files = [f for f in os.listdir(self.photo_dir) if f.lower().endswith('.jpg')]

            csv_headers = ['filename', 'filesize_bytes', 'created_time', 'modified_time']

            with open(self.output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writeheader()

                for photo in photo_files:
                    full_path = os.path.join(self.photo_dir, photo)
                    stat_info = os.stat(full_path)
                    created_time = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
                    modified_time = datetime.fromtimestamp(stat_info.st_mtime).isoformat()

                    writer.writerow({
                        'filename': photo,
                        'filesize_bytes': stat_info.st_size,
                        'created_time': created_time,
                        'modified_time': modified_time
                    })

            logging.info(f"Cataloged {len(photo_files)} photos into {self.output_csv}")
        except Exception as e:
            logging.error(f"Error during photo cataloging: {e}")
            raise
