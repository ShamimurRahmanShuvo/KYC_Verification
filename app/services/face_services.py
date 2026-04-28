import os
import cv2
import uuid
import face_recognition
import numpy as np
from mtcnn import MTCNN
from PIL import Image, ImageOps

detector = MTCNN()

CROP_DIR = "uploads/kyc/cropped_faces"
os.makedirs(CROP_DIR, exist_ok=True)


def load_rgb_image(image_path):
    try:
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        return np.array(image)
    except Exception as e:
        raise Exception(f"Error loading image with EXIF fix: {str(e)}")


def detect_face_locations_with_rotation(rgb):
    """
    Try face detection in multiple orientations to handle cases where the image might be rotated.
    0, 90, 180, 270 degrees.
    """
    rotations = [
        rgb,
        cv2.rotate(rgb, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(rgb, cv2.ROTATE_180),
        cv2.rotate(rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)
    ]

    for rotated in rotations:
        locations = face_recognition.face_locations(rotated, model="hog")
        if locations:
            return rotated, locations

    raise Exception("No face detected in any orientation")


def ensure_single_face(image_path):
    rgb = load_rgb_image(image_path)
    _, locations = detect_face_locations_with_rotation(rgb)

    if len(locations) == 0:
        raise Exception(f"No face detected {image_path}")
    elif len(locations) > 1:
        raise Exception("Multiple faces detected")

    return True


def detect_face(image_path):
    try:
        rgb = load_rgb_image(image_path)
        _, locations = detect_face_locations_with_rotation(rgb)

        return len(locations) > 0
    except Exception as e:
        raise Exception(f"Error during face detection: {str(e)}")


def crop_face_from_document(document_path):
    image = cv2.imread(document_path)

    if image is None:
        raise Exception("Invalid document image")

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    faces = detector.detect_faces(rgb)

    if not faces:
        raise Exception("No face detected in ID document")

    face = max(faces, key=lambda f: f['box'][2] * f['box'][3])

    x, y, w, h = face["box"]

    x = max(0, x)
    y = max(0, y)

    cropped = image[y:y+h, x:x+w]

    file_name = f"cropped_face_{uuid.uuid4().hex}.jpg"
    save_path = os.path.join(CROP_DIR, file_name)

    cv2.imwrite(save_path, cropped)

    return save_path


def get_face_encodings(image_path):
    rgb = load_rgb_image(image_path)

    rotated_img, locations = detect_face_locations_with_rotation(rgb)

    encodings = face_recognition.face_encodings(rotated_img, known_face_locations=locations)

    if not encodings:
        raise Exception("Face detected but no encodings found")

    return encodings[0]


def compare_faces(selfie_path, cropped_document_face_path):
    selfie_encoding = get_face_encodings(selfie_path)
    document_encoding = get_face_encodings(cropped_document_face_path)

    distance = face_recognition.face_distance([document_encoding], selfie_encoding)[0]

    score = max(0, min(100, (1 - distance) * 100))  # Convert distance to a percentage score
    return round(score, 2)


def generate_face_score(selfie_path, document_image_path):
    try:
        ensure_single_face(selfie_path)

        cropped_document_face_path = crop_face_from_document(document_image_path)
        print(f"Selfie: {selfie_path}\n"
              f"Cropped Document Face: {cropped_document_face_path}\n, "
              f"Document: {document_image_path}")
        score = compare_faces(selfie_path, cropped_document_face_path)

        return score

    except Exception as e:
        raise Exception(f"Face comparison failed: {str(e)}")
