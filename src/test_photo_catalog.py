import os
import csv
from photo_catalog import catalog_photos

OUTPUT_CSV = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\outputs\photo_catalog.csv"


def test_catalog_photos():
    # Run the photo cataloging
    catalog_photos()

    # Check if output CSV exists
    assert os.path.exists(OUTPUT_CSV), "Output CSV was not created."

    # Read and print CSV contents for verification
    with open(OUTPUT_CSV, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        print(f"Number of cataloged photos: {len(rows)}")
        for row in rows:
            print(row)


if __name__ == '__main__':
    test_catalog_photos()
