# KYC Verification Microservice

A production-focused KYC verification microservice built with FastAPI. It accepts a selfie and a government ID image, extracts and OCRs ID data, runs face comparison and liveness checks, and stores verification records.

Table of contents
- Overview
- Features
- Tech stack
- Quickstart (local)
- Configuration
- Running
- API reference
- Project structure
- Production notes
- Troubleshooting & tips

## Overview

This service provides endpoints to submit KYC verification requests and to query stored verification records. Processing steps include:
- ID image preprocessing (detect/crop face from ID)
- OCR extraction of fields (name, DOB, ID number)
- Face comparison between selfie and ID face
- Liveness checks to mitigate spoofing
- Persisting verification results and metadata

## Features

- Face verification (selfie vs cropped ID face)
- OCR extraction for ID fields
- Liveness detection hooks
- REST API with auto-generated docs (Swagger / ReDoc)
- SQLite for local development (configurable)
- Pluggable services for storage and background jobs

## Tech stack

- Python 3.10+
- FastAPI
- Uvicorn
- SQLAlchemy (ORM)
- SQLite (default for local development)
- DeepFace / OpenCV / MTCNN (face detection & matching)
- Tesseract OCR
- Pydantic for schemas

## Quickstart (local)

1. Clone the repo and change to the backend folder:

```bash
git clone <your_repo_url>
cd KYC_Verification
```

2. Create and activate a virtual environment:

macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Install system dependencies (Tesseract OCR):

macOS:

```bash
brew install tesseract
```

Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y tesseract-ocr libtesseract-dev
```

Windows: download and install from the official Tesseract project and add to PATH.

## Configuration

Configuration lives in `app/core/config.py`. Common env vars:

- `DATABASE_URL` (default: SQLite file)
- `SECRET_KEY` (used for any token generation)
- `TESSERACT_CMD` (path to `tesseract` binary if non-standard)
- `S3_BUCKET` / `STORAGE_BACKEND` (optional, for cloud storage)

Set env vars locally (example):

```bash
export DATABASE_URL="sqlite:///./kyc.db"
export TESSERACT_CMD="/usr/local/bin/tesseract"
```

## Running

Run with Uvicorn (development):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or run the provided entrypoint:

```bash
python run.py
```

Open API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API reference

POST /kyc/verify
- Description: Submit a verification request with `selfie` and `id_image` files (multipart/form-data).
- Request fields: `selfie` (file), `id_image` (file), optional `metadata` (json)
- Response: verification record including `kyc_id`, `verified` (bool), `match_score` (float), `liveness` (bool), and extracted `data` (name, dob, idn).

Example response:

```json
{
  "kyc_id": 1,
  "verified": true,
  "match_score": 83.46,
  "liveness": true,
  "review_required": false,
  "status": "verified",
  "failure_reason": null,
  "data": {
    "name": "Jane Doe",
    "dob": "1990-01-01",
    "idn": "123456789"
  }
}
```

GET /kyc/records
- Returns a list of stored verification records (use pagination if many records).

Refer to the live Swagger UI for full request/response schemas and example payloads.

## Project structure

- app/
  - main.py                # FastAPI app and startup events
  - core/                  # config, auth helpers, constants
  - models/                # SQLAlchemy models
  - routes/                # API route handlers
  - schemas/               # Pydantic request/response schemas
  - services/              # Business logic (OCR, face, storage, etc.)
  - utils/                 # utility helpers (encryption, logging, pagination)

## Production considerations

- Use a managed DB (Postgres) instead of SQLite for concurrency and reliability.
- Serve with Uvicorn behind a process manager (Gunicorn + Uvicorn workers) or Kubernetes.
- Enable HTTPS and use a secure object storage (S3) for images.
- Encrypt sensitive data at rest and in transit.
- Add authentication (JWT/OAuth2) and RBAC for admin endpoints.
- Add rate limiting, request validation, and structured audit logging.
- Move expensive work (OCR, face matching) to background workers (Celery/RQ).

## Troubleshooting & tips

- Verify Tesseract is installed: `tesseract --version`
- If face detection fails often, ensure images are clear and well-lit.
- For numpy/DeepFace mismatches, pin compatible numpy version if needed.
- Logs are written by `app/core/logger.py` — check logs for stack traces.

## Tests

Add or run unit/integration tests (not included by default). Consider adding tests for:
- OCR extraction logic
- Face comparison thresholds
- API contract tests

## Next steps / Improvements

- Add Dockerfile and docker-compose for local development
- Add CI pipeline with tests and linting
- Add admin UI for review and audit

---