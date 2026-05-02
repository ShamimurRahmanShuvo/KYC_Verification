# Document parsing and processing services
import pytesseract
import cv2
import re


def process_front_document(path: str):
    return extract_document_fields(path)


def process_back_document(path: str):
    # Similar processing for the back of the document, if needed
    return extract_document_fields(path)


def extract_document_fields(image_path: str):
    # Load the image
    image = cv2.imread(image_path)

    # Preprocess the image (grayscale, thresholding)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Use Tesseract to extract text from the image
    text = pytesseract.image_to_string(thresh)

    # Extract fields using regex (example for name and document number)
    name_match = re.search(r'Name:\s*(.*)', text)
    doc_number_match = re.search(r'Document Number:\s*(.*)', text)

    name = name_match.group(1) if name_match else None
    doc_number = doc_number_match.group(1) if doc_number_match else None

    result = {
        'name': name,
        'id_number': doc_number,
        "expiry": None,  # Placeholder for expiry date extraction
        "raw_text": text  # Include raw text for debugging purposes
    }

    return result


def check_expiry(expiry_date: str):
    return False


def detect_document_type(image_path: str):
    return "Govt ID"
