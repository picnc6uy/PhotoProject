import cv2
import numpy as np
import math

def detect_circles(image_gray):
    """Detect circles in the grayscale image using Hough Circle Transform."""
    blurred = cv2.medianBlur(image_gray, 5)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=100,
        param2=30,
        minRadius=100,
        maxRadius=0
    )
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        return circles
    return []

def unwrap_circular_text(image, center, radius, thickness=40):
    """
    Unwrap the circular text band defined by center, radius and thickness into a rectangular image.
    - center: (x, y)
    - radius: approximate middle radius of circular text band
    - thickness: radial thickness of text band to capture
    """
    # Parameters for unwrapped image
    height = thickness
    width = int(2 * math.pi * radius)
    unwrapped = np.zeros((height, width, 3), dtype=np.uint8)

    for i in range(width):
        theta = (float(i) / width) * 2.0 * math.pi  # angle in radians
        for j in range(height):
            r = radius - thickness//2 + j
            x = int(center[0] + r * math.cos(theta))
            y = int(center[1] + r * math.sin(theta))
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                unwrapped[j, i] = image[y, x]
            else:
                unwrapped[j, i] = 0

    return unwrapped

def preprocess_for_ocr(image):
    """Convert to grayscale and apply adaptive thresholding for OCR readiness."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 15, 10
    )
    return thresh

def main(image_path):
    # Load image and convert to grayscale
    image = cv2.imread(image_path)
    if image is None:
        print("Error loading image:", image_path)
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect circles representing labels
    circles = detect_circles(gray)
    if len(circles) == 0:
        print("No circles detected.")
        return

    # Draw detected circles on a copy for visualization
    vis_image = image.copy()
    for (x, y, r) in circles:
        cv2.circle(vis_image, (x, y), r, (0, 255, 0), 2)
        cv2.circle(vis_image, (x, y), 2, (0, 0, 255), 3)  # center point

    cv2.imshow("Detected Circles", vis_image)
    cv2.waitKey(0)

    # For demo: pick the largest circle (assumed main label)
    largest_circle = max(circles, key=lambda c: c[2])
    center = (largest_circle[0], largest_circle[1])
    radius = largest_circle[2]

    # Unwrap circular text (you may adjust thickness based on label)
    unwrapped_img = unwrap_circular_text(image, center, radius, thickness=50)
    cv2.imshow("Unwrapped Circular Text", unwrapped_img)
    cv2.waitKey(0)

    # Preprocess for OCR (thresholding)
    preprocessed_ocr_img = preprocess_for_ocr(unwrapped_img)
    cv2.imshow("Preprocessed for OCR", preprocessed_ocr_img)
    cv2.waitKey(0)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python circular_label_ocr.py <path_to_image>")
    else:
        main(sys.argv[1])
