import os
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from io import BytesIO
from PIL import Image

# Environment variables for security
subscription_key = os.getenv("AZURE_COMPUTER_VISION_KEY")
endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")

client = ComputerVisionClient(endpoint=endpoint, credentials=CognitiveServicesCredentials(subscription_key))

# Folder with preprocessed, resized images for OCR
ocr_folder = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos_ocr"

def resize_and_reencode_image(image_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            return output
    except Exception as e:
        print(f"Error re-encoding {os.path.basename(image_path)}: {e}")
        return None

def ocr_local_image(image_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            img_stream = resize_and_reencode_image(image_path)
            if img_stream is None:
                return ""
            ocr_result = client.read_in_stream(img_stream, raw=True)
            operation_location = ocr_result.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]

            while True:
                result = client.get_read_result(operation_id)
                if result.status.lower() not in ["notstarted", "running"]:
                    break
                time.sleep(1)

            if result.status == "succeeded":
                text = [line.text for page in result.analyze_result.read_results for line in page.lines]
                return "\n".join(text)
            else:
                return ""
        except Exception as e:
            print(f"OCR attempt {attempt+1} failed for {os.path.basename(image_path)}: {e}")
            time.sleep(2 ** attempt)  # exponential backoff
    return ""

if __name__ == "__main__":
    results = []

    for filename in sorted(os.listdir(ocr_folder)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            image_path = os.path.join(ocr_folder, filename)
            try:
                ocr_text = ocr_local_image(image_path)
                print(f"{filename}: {len(ocr_text)} characters extracted")
                results.append((filename, ocr_text))
            except Exception as e:
                print(f"Error processing {filename}: {e}")

            time.sleep(5)  # delay to respect rate limits

    import csv
    output_csv = os.path.join(ocr_folder, "azure_ocr_results.csv")
    with open(output_csv, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "ocr_text"])
        writer.writerows(results)

    print(f"OCR results saved to {output_csv}")

# This file has been archived and renamed to src/archive/azure_read_ocr_from_resized.py
# To reduce clutter, this file should no longer be used in active development.
# Archived as per cleanup decision for Azure OCR script consolidation.
