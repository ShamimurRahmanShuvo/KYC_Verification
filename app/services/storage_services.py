import os
import shutil
from uuid import uuid4
from app.utils.validators import validate_image_type, validate_video_type

UPLOAD_DIR = "uploads"


def save_uploads(file, folder="temp"):
    full_dir = os.path.join(UPLOAD_DIR, folder)
    if not os.path.exists(full_dir):
        os.makedirs(f"{UPLOAD_DIR}/{folder}", exist_ok=True)

    unique_id = str(uuid4())

    if validate_image_type(file.filename):
        ext = file.filename.split(".")[-1].lower()
        filename = f"{unique_id}.{ext}"
    elif validate_video_type(file.filename):
        ext = file.filename.split(".")[-1].lower()
        filename = f"{unique_id}.{ext}"
    else:
        raise Exception("Unsupported file type")

    path = f"{UPLOAD_DIR}/{folder}/{filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return path


def save_temp_file(file):
    return save_uploads(file, folder="temp")


def move_file(src_path, folder):
    final_dir = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(final_dir, exist_ok=True)

    filename = os.path.basename(src_path)
    final_path = os.path.join(final_dir, filename)

    if os.path.exists(final_path):
        os.remove(final_path)

    os.replace(src_path, final_path)
    return final_path


def delete_file(path):
    if path and os.path.exists(path):
        os.remove(path)


def purge_expired_biometrics():
    temp_dir = f"{UPLOAD_DIR}/temp"
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
