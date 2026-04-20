import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = "sqlite:///./kyc.db"
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")


settings = Settings()
