import os
import time
import logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

class OCRService:
    """Encapsulates interactions with Azure OCR or other OCR providers."""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        subscription_key = config.get("AZURE_COMPUTER_VISION_KEY")
        endpoint = config.get("AZURE_COMPUTER_VISION_ENDPOINT")
        self.subscription_key = subscription_key
        self.endpoint = endpoint
        self.client = ComputerVisionClient(endpoint=endpoint, credentials=CognitiveServicesCredentials(subscription_key))

    def submit_image_for_ocr(self, image_path: str) -> str:
        self.logger.info("Using Azure endpoint: %s", self.endpoint)
        self.logger.info(
            "Using Azure subscription key: %s",
            ('***' + str(self.subscription_key)[-4:]) if self.subscription_key else None
        )
        try:
            with open(image_path, 'rb') as img_stream:
                ocr_result = self.client.read_in_stream(img_stream, raw=True)
        except Exception as e:
            self.logger.error("Error submitting image %s for OCR: %s", image_path, e)
            return ""

        if not ocr_result or not hasattr(ocr_result, 'headers'):
            self.logger.error("Invalid response from OCR service for %s", image_path)
            return ""
        operation_location = ocr_result.headers.get("Operation-Location", "")
        operation_id = operation_location.split("/")[-1] if operation_location else ""
        return operation_id

    def get_ocr_results(self, operation_id: str) -> dict:
        """Poll for OCR results until complete."""
        max_retries = self.config.get("MAX_OCR_RETRIES", 10)
        delay_seconds = self.config.get("OCR_RETRY_DELAY", 1)

        for _ in range(max_retries):
            result = self.client.get_read_result(operation_id)
            if result.status.lower() not in ["notstarted", "running"]:
                return result
            time.sleep(delay_seconds)
        return None

    def process_image(self, image_path: str) -> dict:
        """End-to-end process: submit image and get full OCR results including details."""
        operation_id = self.submit_image_for_ocr(image_path)
        if not operation_id:
            return {}
        result = self.get_ocr_results(operation_id)
        if result and result.status == "succeeded":
            # Parse rich OCR results
            parsed_results = []
            for page in result.analyze_result.read_results:
                for line in page.lines:
                    words_info = []
                    for word in line.words:
                        words_info.append({
                            'text': word.text,
                            'confidence': getattr(word, 'confidence', None),
                            'bounding_box': [
                                {'x': point.x, 'y': point.y} for point in getattr(word, 'bounding_polygon', [])
                            ]
                        })
                    parsed_results.append({
                        'text': line.text,
                        'words': words_info,
                        'bounding_box': [
                            {'x': point.x, 'y': point.y} for point in getattr(line, 'bounding_polygon', [])
                        ]
                    })
            text = "\n".join([line.get('text', '') for line in parsed_results if line.get('text')])
            return {
                'pages': len(result.analyze_result.read_results),
                'lines': parsed_results,
                'raw_result': result,
                'text': text
            }
        return {}

    def get_text_with_confidence_filter(self, ocr_data: dict, threshold: float = 0.8) -> str:
        """Return concatenated text keeping words above confidence threshold."""
        if not ocr_data or 'lines' not in ocr_data:
            return ""
        texts = []
        for line in ocr_data['lines']:
            filtered_words = [w['text'] for w in line['words'] if w.get('confidence', 1.0) >= threshold]
            if filtered_words:
                texts.append(' '.join(filtered_words))
        return '\n'.join(texts)
