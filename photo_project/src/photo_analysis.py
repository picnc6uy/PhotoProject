import os
import cv2

# Directory containing photos (should match your catalog input folder)
PHOTO_DIR = r"C:/Users/ghendrick/PhotoProject/dev_data/record_catalog/data/inbox_photos"

def analyze_photos():
    # List photo files
    photo_files = [f for f in os.listdir(PHOTO_DIR) if f.lower().endswith('.jpg')]

    for photo in photo_files:
        photo_path = os.path.join(PHOTO_DIR, photo)
        img = cv2.imread(photo_path)

        if img is None:
            print(f"Failed to load {photo_path}")
            continue

        # Simple analysis: print image dimensions
        height, width, channels = img.shape
        print(f"{photo}: width={width}, height={height}, channels={channels}")

        # TODO: Add more OpenCV processing here (e.g., feature detection)

if __name__ == '__main__':
    analyze_photos()