# Sensitive Data Protection
import os
import hashlib
import base64
from cryptography.fernet import Fernet

# env variable from production should be used to set the key
SECRET_KEY = os.getenv("SECRET_KEY", Fernet.generate_key())
cipher = Fernet(SECRET_KEY)


# Encrypts PII before storing it in the database and decrypts it when needed.
def encrypt_text(plain_text: str) -> str:
    # Placeholder for encryption logic (e.g., using Fernet or AES)
    if not plain_text:
        return ""
    token = cipher.encrypt(plain_text.encode())

    return token.decode()


def decrypt_text(encrypted_text: str) -> str:
    # Placeholder for decryption logic
    if not encrypted_text:
        return ""
    decrypted = cipher.decrypt(encrypted_text.encode())
    return decrypted.decode()


# Hash identifiers like email or phone number for indexing and searching without exposing raw values.
def hash_identifier(identifier: str) -> str:
    if not identifier:
        return ""
    # Using SHA-256 for hashing
    return hashlib.sha256(identifier.encode()).hexdigest()
