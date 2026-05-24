from uuid import uuid4
from datetime import datetime


def generate_case_reference():
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid4())[:8]
    return f"CASE-{timestamp}-{unique_id}"
