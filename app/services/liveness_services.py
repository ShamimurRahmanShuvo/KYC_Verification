import cv2
from app.services.face_services import detect_face, ensure_single_face


def passive_liveness_check(image_path):
    """
    Uses face detection services
    Rules:
    - Image readable
    - Contains exactly one face
    - No multiple faces
    """
    try:
        if not detect_face(image_path):
            return False

        ensure_single_face(image_path)
        return True

    except Exception as e:
        raise Exception(f"Passive liveness check failed: {str(e)}")


def active_liveness_check(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("Could not open video")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise Exception("Could not read video frame")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    edge_count = cv2.countNonZero(edges)

    return edge_count > 1000


def video_processing(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("Could not open video")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise Exception("Could not read video frame")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    return gray


def blink_detection(video_path):
    gray = video_processing(video_path)
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    return len(eyes) >= 1


def head_turn_detection(video_path):
    gray = video_processing(video_path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    return len(faces) > 0


def combined_liveness_score(image_path, video_path):
    passive_score = passive_liveness_check(image_path)

    if video_path:
        active_score = active_liveness_check(video_path)
        blink_score = blink_detection(video_path)
        head_turn_score = head_turn_detection(video_path)

        total_score = (passive_score + active_score + blink_score + head_turn_score) / 4 * 100

        return round(total_score, 2)
    return round(passive_score * 100, 2)
