# Pre-checks image and video quality before validation
from typing import Tuple

import cv2
import numpy as np


def detect_blur(image_path: str) -> float:
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var


def detect_glare(image_path: str) -> float:
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bright_pixels = np.sum(gray > 240)  # Count pixels that are very bright
    total_pixels = gray.size
    glare_percentage = (bright_pixels / total_pixels) * 100
    return glare_percentage


def detect_document_edges(image_path: str) -> bool:
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours) > 0  # Return True if document edges are detected


def validate_selfie_quality(image_path: str) -> Tuple[bool, str]:
    img = cv2.imread(image_path)

    if img is None:
        return False, "Invalid image. Please retake the selfie."

    h, w = img.shape[:2]

    if w < 250 or h < 250:
        return False, "Image resolution is too low. Please retake the selfie with a higher resolution."

    blur = detect_blur(image_path)

    if blur < 80:
        return False, "Image is too blurry. Please retake the selfie."

    return True, "Selfie quality is acceptable."


def validate_document_quality(image_path: str) -> Tuple[bool, str]:
    blur = detect_blur(image_path)
    glare = detect_glare(image_path)
    edges = detect_document_edges(image_path)

    if blur < 80:
        return False, "Doc is too blurry. Please retake the document photo."

    if glare > 20:
        return False, "Doc has too much glare. Please retake the document photo."

    if not edges:
        return False, "Document edges not detected. Please ensure the document is fully visible and retake the photo."

    return True, "Document quality is acceptable."
