import cv2
import os

# Define test image path to inbox_photos directory
workspace_root = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(workspace_root, '..', 'dev_data', 'record_catalog', 'data', 'inbox_photos')

# Find first image file in the inbox_photos directory
image_file = None
for f in os.listdir(image_path):
    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        image_file = os.path.join(image_path, f)
        break

if image_file is None:
    print('No image file found in inbox_photos to test opencv.')
else:
    print(f'Reading image file {image_file}')
    img = cv2.imread(image_file)
    if img is None:
        print('Failed to read image with opencv.')
    else:
        print(f'Image shape: {img.shape}')
        print('OpenCV test successful.')