from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import os

import os

subscription_key = os.environ.get("AZURE_COMPUTER_VISION_KEY", "")

endpoint = "https://photocatalog.cognitiveservices.azure.com/"

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def describe_local_image(image_path):
    with open(image_path, "rb") as img_stream:
        description_result = client.describe_image_in_stream(img_stream)
    if description_result.captions:
        for caption in description_result.captions:
            print(f'Description: {caption.text} (confidence: {caption.confidence:.2f})')
    else:
        print("No description detected.")

if __name__ == "__main__":
    image_path = r"C:\Users\ghendrick\PhotoProject\dev_data\record_catalog\data\inbox_photos\photo_0001.jpg"
    describe_local_image(image_path)