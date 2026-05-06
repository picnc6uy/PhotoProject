# This file has been archived and renamed to src/archive/azure_batch_describe.py
# To reduce clutter, this file should no longer be used in active development.
# Archived as per cleanup decision for Azure OCR script consolidation.

import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image
from io import BytesIO
import time

import os

subscription_key = os.environ.get("AZURE_COMPUTER_VISION_KEY", "")

endpoint = "https://photocatalog.cognitiveservices.azure.com/"

client = ComputerVisionClient(endpoint=endpoint, credentials=CognitiveServicesCredentials(subscription_key))

def resize_image_for_azure(image_path, max_dimension=3500):
    with Image.open(image_path) as img:
        width, height = img.size
        max_side = max(width, height)
        scale = min(1.0, max_dimension / max_side)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        byte_arr = BytesIO()
        img.save(byte_arr, format='JPEG', quality=75)
        byte_arr.seek(0)
        return byte_arr

def describe_local_image(image_path):
    img_stream = resize_image_for_azure(image_path)
    description_result = client.describe_image_in_stream(img_stream)
    if description_result.captions:
        return description_result.captions[0].text, description_result.captions[0].confidence
    else:
        return "No description detected.", 0.0

if __name__ == "__main__":
    folder_path = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos_resized"
    descriptions = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            image_path = os.path.join(folder_path, filename)
            desc, conf = describe_local_image(image_path)
            print(f"{filename}: {desc} (confidence: {conf:.2f})")
            descriptions.append((filename, desc, conf))
            time.sleep(1)  # Throttle to avoid hitting API limits

    import csv
    output_csv = os.path.join(folder_path, 'image_descriptions.csv')
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'description', 'confidence'])
        writer.writerows(descriptions)

    print(f"Descriptions saved to {output_csv}")