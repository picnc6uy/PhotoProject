import os
import csv
from datetime import datetime

# Define paths
PHOTO_DIR = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos"
OUTPUT_CSV = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\outputs\photo_catalog.csv"


def catalog_photos():
    # Gather photo files
    photo_files = [f for f in os.listdir(PHOTO_DIR) if f.lower().endswith('.jpg')]

    # Prepare csv headers
    csv_headers = ['filename', 'filesize_bytes', 'created_time', 'modified_time']

    # Write CSV
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()

        for photo in photo_files:
            full_path = os.path.join(PHOTO_DIR, photo)
            stat_info = os.stat(full_path)
            created_time = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
            modified_time = datetime.fromtimestamp(stat_info.st_mtime).isoformat()

            writer.writerow({
                'filename': photo,
                'filesize_bytes': stat_info.st_size,
                'created_time': created_time,
                'modified_time': modified_time
            })

    print(f"Cataloged {len(photo_files)} photos into {OUTPUT_CSV}")


if __name__ == '__main__':
    catalog_photos()
