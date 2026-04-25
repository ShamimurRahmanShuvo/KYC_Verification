import cv2
import face_recognition


def detect_face(image_path):
    image = face_recognition.load_image_file(image_path)
    locations = face_recognition.face_locations(image)
    return len(locations) > 0


def ensure_single_face(image_path):
    image = face_recognition.load_image_file(image_path)
    locations = face_recognition.face_locations(image)
    if len(locations) == 0:
        raise Exception("No face detected")
    elif len(locations) > 1:
        raise Exception("Multiple faces detected")
    return True


def crop_face_from_document(image_path, save_path):
    image = cv2.imread(image_path)

    if image is None:
        raise Exception("Invalid image")

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    faces = detector.detect_faces(rgb)

    if not faces:
        raise Exception("No face detected")

    x, y, w, h = faces[0]["box"]

    x = max(0, x)
    y = max(0, y)

    cropped = image[y:y+h, x:x+w]

    cv2.imwrite(save_path, cropped)

    return save_path


def compare_faces(selfie_path, document_image_path):
    selfie_image = face_recognition.load_image_file(selfie_path)
    document_image = face_recognition.load_image_file(document_image_path)

    selfie_encodings = face_recognition.face_encodings(selfie_image)
    document_encodings = face_recognition.face_encodings(document_image)

    if not selfie_encodings:
        raise Exception("No face detected in selfie")
    if not document_encodings:
        raise Exception("No face detected in document")

    selfie_encoding = selfie_encodings[0]
    document_encoding = document_encodings[0]

    results = face_recognition.face_distance([document_encoding[0]], selfie_encoding[0])[0]
    score = (1 - results) * 100  # Convert distance to a percentage score
    return round(score, 2)


def generate_face_score(selfie_path, document_image_path):
    try:
        ensure_single_face(selfie_path)
        ensure_single_face(document_image_path)

        cropped_document_face = crop_face_from_document(document_image_path, "cropped_face.jpg")
        score = compare_faces(selfie_path, cropped_document_face)

        return score
    except Exception as e:
        raise Exception(f"Face comparison failed: {str(e)}")
