import os
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# Environment variables for Azure credentials
subscription_key = os.getenv("AZURE_COMPUTER_VISION_KEY")
endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")

client = ComputerVisionClient(endpoint=endpoint, credentials=CognitiveServicesCredentials(subscription_key))

ocr_folder = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos_ocr"

def is_image_file_valid(image_path):
    try:
        # Simple check by trying to open via PIL
        from PIL import Image
        with Image.open(image_path) as img:
            img.verify()  # Verify not corrupted
        return True
    except Exception as e:
        print(f"Invalid image file {os.path.basename(image_path)}: {e}")
        return False

def ocr_local_image(image_path):
    with open(image_path, "rb") as img_stream:
        read_response = client.read_in_stream(img_stream, raw=True)
    operation_location = read_response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    while True:
        result = client.get_read_result(operation_id)
        if result.status.lower() not in ["notstarted", "running"]:
            break
        time.sleep(1)

    if result.status == "succeeded":
        texts = []
        for page in result.analyze_result.read_results:
            for line in page.lines:
                texts.append(line.text)
        return "\n".join(texts)
    else:
        return ""

if __name__ == "__main__":
    results = []

    for filename in sorted(os.listdir(ocr_folder)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            image_path = os.path.join(ocr_folder, filename)

            if not is_image_file_valid(image_path):
                continue

            try:
                ocr_text = ocr_local_image(image_path)
                print(f"{filename}: {len(ocr_text)} characters extracted")
                results.append((filename, ocr_text))
            except Exception as e:
                print(f"Error during OCR for {filename}: {e}")

            time.sleep(5)  # pause to respect Azure rate limits

    import csv
    output_csv = os.path.join(ocr_folder, "azure_ocr_results_simple.csv")
    with open(output_csv, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "ocr_text"])
        writer.writerows(results)

    print(f"OCR results saved to {output_csv}")

# This file has been archived and renamed to src/archive/azure_read_ocr_simple.py
# To reduce clutter, this file should no longer be used in active development.
# Archived as per cleanup decision for Azure OCR script consolidation.
