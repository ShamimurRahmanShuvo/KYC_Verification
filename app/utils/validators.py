# In this file, we will define some validators for our application.
import os


ALLOWED_IMAGE_TYPES = [".jpeg", ".png", ".gif"]
ALLOWED_VIDEO_TYPES = [".mp4", ".avi", ".mov", ".mkv"]


def validate_image_type(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_IMAGE_TYPES


def validate_video_type(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_VIDEO_TYPES


def validate_file_size(file, max_size_mb: int) -> bool:
    file.seek(0, os.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    return size_mb <= max_size_mb


def validate_country_code(country_code: str) -> bool:
    if not country_code:
        return False
    return len(country_code) == 2 and country_code.isalpha()
