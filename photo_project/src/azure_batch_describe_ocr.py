import os
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from io import BytesIO
from PIL import Image

# This file has been archived and renamed to src/archive/azure_batch_describe_ocr.py
# To reduce clutter, this file should no longer be used in active development.
# Archived as per cleanup decision for Azure OCR script consolidation.

import os

subscription_key = os.environ.get("AZURE_COMPUTER_VISION_KEY", "")

endpoint = "https://photocatalog.cognitiveservices.azure.com/"

client = ComputerVisionClient(endpoint=endpoint, credentials=CognitiveServicesCredentials(subscription_key))

desc_folder = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos_desc"
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

def describe_local_image(filepath, max_retries=3):
    for attempt in range(max_retries):
        try:
            img_stream = resize_and_reencode_image(filepath)
            if img_stream is None:
                return "Description failed due to image error.", 0.0
            description_result = client.describe_image_in_stream(img_stream)
            if description_result.captions:
                return description_result.captions[0].text, description_result.captions[0].confidence
            else:
                return "No description detected.", 0.0
        except Exception as e:
            print(f"Describe attempt {attempt+1} failed for {os.path.basename(filepath)}: {e}")
            time.sleep(3 * (attempt + 1))
    return "Description failed after retries.", 0.0

def ocr_local_image(filepath, max_retries=3):
    for attempt in range(max_retries):
        try:
            img_stream = resize_and_reencode_image(filepath)
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
            print(f"OCR attempt {attempt+1} failed for {os.path.basename(filepath)}: {e}")
            time.sleep(3 * (attempt + 1))
    return ""

if __name__ == "__main__":
    results = []

    desc_files = set(os.listdir(desc_folder))
    ocr_files = set(os.listdir(ocr_folder))
    common_files = desc_files.intersection(ocr_files)

    for idx, filename in enumerate(sorted(common_files)):
        desc_path = os.path.join(desc_folder, filename)
        ocr_path = os.path.join(ocr_folder, filename)

        desc_text, desc_conf = describe_local_image(desc_path)
        ocr_text = ocr_local_image(ocr_path)
        print(f"{filename}:\n Description: {desc_text} (confidence: {desc_conf:.2f})\n OCR Text:\n{ocr_text}\n")
        results.append((filename, desc_text, desc_conf, ocr_text))

        time.sleep(5)  # Increased delay to 5 seconds to avoid rate limiting

    import csv
    output_csv = os.path.join(desc_folder, "image_descriptions_ocr.csv")
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "description", "confidence", "ocr_text"])
        writer.writerows(results)

    print(f"Results saved to {output_csv}")