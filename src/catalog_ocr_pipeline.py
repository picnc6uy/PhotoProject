import os
import cv2
import numpy as np
import pytesseract
import pandas as pd

# Configure this path if Tesseract is not in your PATH environment variable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Paths
workspace_root = os.path.dirname(os.path.abspath(__file__))
catalog_csv_path = os.path.join(workspace_root, '..', 'dev_data', 'record_catalog', 'data', 'outputs', 'photo_catalog.csv')
images_dir = os.path.join(workspace_root, '..', 'dev_data', 'record_catalog', 'data', 'inbox_photos')

# Load the catalog CSV
df = pd.read_csv(catalog_csv_path)

def preprocess_image(img_path):
    img = cv2.imread(img_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply median blur to reduce noise
    blurred = cv2.medianBlur(gray, 3)

    # Apply Otsu's thresholding to binarize image
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Optional: resize image if too small (e.g., width < 800 px)
    h, w = thresh.shape
    if w < 800:
        scale = 800 / w
        thresh = cv2.resize(thresh, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    return thresh

def extract_ocr_text(image_path):
    img = preprocess_image(image_path)
    if img is None:
        return None

    # Configure tesseract settings: OCR engine mode=3 (LSTM + legacy), PSM=6 (single block)
    custom_config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(img, config=custom_config)
    if text:
        text = text.strip()
    return text

ocr_texts = []
for idx, row in df.iterrows():
    image_file = row['filename']
    image_path = os.path.join(images_dir, image_file)
    ocr_result = extract_ocr_text(image_path)
    if ocr_result is None or len(ocr_result) == 0:
        ocr_texts.append('No text found')
    elif len(ocr_result) > 500:
        ocr_texts.append(ocr_result)
    else:
        ocr_texts.append('')  # No or short text - leave empty

df['ocr_text'] = ocr_texts

# Save to a new CSV file with '_ocr' suffix
output_csv_path = os.path.join(os.path.dirname(catalog_csv_path), 'photo_catalog_ocr.csv')
df.to_csv(output_csv_path, index=False)
print(f'OCR augmented catalog saved to {output_csv_path}')