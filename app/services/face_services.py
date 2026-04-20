from deepface import DeepFace


def compare_faces(selfie_path, id_path):
    result = DeepFace.verify(
        img1_path=selfie_path,
        img2_path=id_path,
        enforce_detection=False
    )

    score = (1 - result["distance"]) * 100
    return round(score, 2)
