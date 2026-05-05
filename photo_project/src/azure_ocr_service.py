import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

class AzureOCRService:
    def __init__(self, subscription_key: str, endpoint: str, max_retries: int = 10, retry_delay: float = 1.0):
        self.subscription_key = subscription_key
        self.endpoint = endpoint
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = ComputerVisionClient(endpoint=endpoint, credentials=CognitiveServicesCredentials(subscription_key))

    def submit_image(self, image_path: str) -> str:
        """Submit an image file to Azure OCR and return the operation ID."""
        try:
            with open(image_path, 'rb') as image_stream:
                response = self.client.read_in_stream(image_stream, raw=True)
            operation_location = response.headers.get('Operation-Location')
            operation_id = operation_location.split('/')[-1] if operation_location else ''
            if not operation_id:
                raise RuntimeError('No operation ID received from Azure OCR service')
            return operation_id
        except Exception as e:
            print(f"Error submitting image for OCR: {e}")
            return ''

    def get_read_result(self, operation_id: str) -> dict:
        """Poll Azure OCR service until the operation completes or max retries reached."""
        for attempt in range(self.max_retries):
            result = self.client.get_read_result(operation_id)
            if result.status.lower() not in ('notstarted', 'running'):
                return result
            time.sleep(self.retry_delay)
        raise TimeoutError('Azure OCR operation timed out')

    def extract_text(self, read_result) -> str:
        """Extract and concatenate text lines from Azure OCR read result."""
        if not read_result or read_result.status != 'succeeded':
            return ''
        lines = []
        for page in read_result.analyze_result.read_results:
            for line in page.lines:
                lines.append(line.text)
        return '\n'.join(lines)

    def recognize_text_from_image(self, image_path: str) -> str:
        """Convenience method for full OCR from image file path."""
        operation_id = self.submit_image(image_path)
        if not operation_id:
            return ''
        try:
            result = self.get_read_result(operation_id)
            return self.extract_text(result)
        except TimeoutError as e:
            print(f"Timeout waiting for OCR results: {e}")
            return ''

# End of AzureOCRService

