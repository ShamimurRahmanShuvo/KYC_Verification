from pyzbar.pyzbar import decode
import cv2


def parse_pdf417(image_path):
    image = cv2.imread(image_path)
    codes = decode(image)

    for code in codes:
        if code.type == 'PDF417':
            return code.data.decode('utf-8')

    return None


def parse_qr_code(image_path):
    return parse_pdf417(image_path)


def normalize_barcode_data(data):
    # Implement any normalization logic if needed
    return {
        "barcode_raw": data,
    }
