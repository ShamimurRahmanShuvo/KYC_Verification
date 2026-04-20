import pytesseract
from PIL import Image
import re


def extract_kyc_data(path):
    img = Image.open(path)
    text = pytesseract.image_to_string(img)

    name = re.findall(r'Name[: ](.*)', text)
    dob = re.findall(r'DOB[: ](.*)', text)
    idn = re.findall(r'ID[: ](.*)', text)

    return {
        "name": name[0].strip() if name else "",
        "dob": dob[0].strip() if dob else "",
        "idn": idn[0].strip() if idn else ""
    }
