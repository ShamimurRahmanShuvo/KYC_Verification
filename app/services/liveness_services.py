import cv2
import numpy as np


def check_liveness(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    variance = cv2.Laplacian(gray, cv2.CV_64F).var()

    # blurry or screen replay images often low variance
    if variance < 80:
        return False

    return True
