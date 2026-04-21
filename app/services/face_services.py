import cv2
from deepface import DeepFace
from mtcnn import MTCNN

detector = MTCNN()


def crop_face_from_image(image_path, save_path):
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


def compare_faces(selfie_path, cropped_face_path):
    result = DeepFace.verify(
        img1_path=selfie_path,
        img2_path=cropped_face_path,
        enforce_detection=False
    )

    score = round((1 - result["distance"]) * 100, 2)

    return {
        "verified": result["verified"],
        "score": score
    }
