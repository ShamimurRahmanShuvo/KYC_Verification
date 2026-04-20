# KYC Verification Microservice

Production-ready local KYC verification service built with **FastAPI**, **SQLite**, **Face Recognition**, and **OCR**.
This service allows users to upload:
- A live selfie photo
- A government-issued ID image

The system then:
1. Extracts text from the ID using OCR
2. Compares the face on the ID with the uploaded selfie
3. Generates a match score
4. Marks verification status (`verified` if score >= threshold)
5. Stores results in SQLite
---

# Tech Stack
- FastAPI
- SQLite
- SQLAlchemy
- DeepFace
- OpenCV
- Tesseract OCR
- Pydantic
- Uvicorn
---

# Features
- Face verification (Selfie vs ID)
- OCR extraction from ID card
- SQLite local database
- REST API with Swagger docs
- File upload support
- Persistent KYC records
- Easy local setup

# Installation
1. Clone Project
git clone <your_repo_url>
cd kyc-service

2. Create Virtual Environment

macOS / Linux
- python3 -m venv venv
- source venv/bin/activate

Windows
- python -m venv venv
- venv\Scripts\activate

3. Install Dependencies
- pip install -r requirements.txt
- Install Tesseract OCR

macOS

- brew install tesseract

Ubuntu
- sudo apt install tesseract-ocr

Windows
- Install from official binary package.

Run Application
python run.py

or

uvicorn app.main:app --reload
API Documentation

Swagger UI:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc
API Endpoints
POST /kyc/verify

Upload selfie and ID card for verification.

Example Response

{
  "kyc_id": 1,
  "verified": true,
  "match_score": 91.7,
  "data": {
    "name": "John Smith",
    "dob": "1992-05-12",
    "id_number": "A123456"
  }
}

GET /kyc/records

Returns all stored KYC verification records.


# Verification Logic

Face comparison uses DeepFace.

score = (1 - distance) * 100

verified = score >= 75

Threshold can be customized.

# Important Notes

Current version compares:

- Selfie image
- Full ID card image

# Recommended production upgrade:

Detect face on ID
Crop face region
Compare cropped face vs selfie
Security Recommendations

# For real production use:

- Encrypt uploaded images
- Delete temp files after processing
- Add JWT authentication
- Add rate limiting
- Add audit logs
- Mask sensitive data
- Use PostgreSQL instead of SQLite
- Add HTTPS
- Troubleshooting
- DetachedInstanceError

**Install OCR engine and verify:**

- tesseract --version
- Face Recognition Errors

**Use supported image types:**

- jpg
- jpeg
- png

Ensure image contains visible face.

NumPy Dependency Conflict
pip install numpy==1.26.4
# Future Improvements
- Liveness Detection
- Anti-spoofing
- Passport MRZ Parsing
- Multi-language OCR
- Admin Dashboard
- Docker Support
- Async SQLAlchemy
- Celery Background Jobs
- AWS S3 File Storage
