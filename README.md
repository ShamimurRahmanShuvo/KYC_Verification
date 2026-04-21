# KYC Verification Microservice

Production-ready local KYC verification service built with **FastAPI**, **SQLite**, **Face Recognition**, and **OCR**.
This service allows users to upload:
- A live selfie photo
- A government-issued ID image

The system then:
User uploads a selfie photo
1. User uploads a government-issued ID 
2. Detects and crops face from the ID card 
3. Compares selfie vs ID face using facial recognition 
4. Performs liveness detection to reduce spoofing attempts 
5. Extracts ID data using OCR (Name, DOB, ID Number)
6. Generates match score and verification result 
7. Stores records securely in database
---

# Tech Stack
- FastAPI
- Python
- SQLite
- SQLAlchemy
- DeepFace
- OpenCV
- Tesseract OCR
- Pydantic
- Uvicorn
- REST APIs
---

# Features
- Face verification (Selfie vs ID (Cropped image))
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
- Install mediapipe
- Install mtcnn

macOS

- brew install tesseract

Ubuntu
- sudo apt install tesseract-ocr

Windows
- Install from official binary package.

**Run Application**

python run.py

or

uvicorn app.main:app --reload

**API Documentation**

Swagger UI:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc

**API Endpoints**
POST /kyc/verify

Upload selfie and ID card for verification.

Example Response

{
  "kyc_id": 1,
  "verified": true,
  "match_score": 83.46,
  "liveness": true,
  "review_required": false,
  "status": "verified",
  "failure_reason": None,
  "data": {
    "name": "Md Shamimur Rahman Shuvo",
    "dob": "28th August ...",
    "idn": "123456789"
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
- Cropped image from ID card

# Recommended production upgrade:

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
- Blink Detection
- Head Turn Challenge
- Anti-spoofing
- Passport MRZ Parsing
- Multi-language OCR
- Admin Dashboard
- Docker Support
- Async SQLAlchemy
- Celery Background Jobs
- AWS S3 File Storage
