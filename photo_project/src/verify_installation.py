import cv2
import numpy as np

def verify_installation():
    print(f"OpenCV version: {cv2.__version__}")
    print(f"NumPy version: {np.__version__}")

if __name__ == '__main__':
    verify_installation()