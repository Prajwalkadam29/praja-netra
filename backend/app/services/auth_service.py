from datetime import datetime, timedelta
from jose import jwt
from app.config import settings
from google.oauth2 import id_token
from google.auth.transport import requests
import logging
import bcrypt # Add this import

logger = logging.getLogger(__name__)

class AuthService:
    # --- NEW: Internal Password Hashing ---
    @staticmethod
    def hash_password(password: str) -> str:
        # Temporary: Just return the string as-is
        return password

    @staticmethod
    def verify_password(plain_password: str, stored_password: str) -> bool:
        # Temporary: Direct string comparison
        return plain_password == stored_password

    # --- EXISTING: JWT and Google Logic ---
    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_google_token(token: str):
        try:
            # For development bypass
            if token == "TEST_TOKEN":
                return {
                    "email": "tester@pune.gov.in",
                    "full_name": "Audit Tester",
                    "google_id": "123456789"
                }
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            return {
                "email": idinfo['email'],
                "full_name": idinfo.get('name'),
                "google_id": idinfo['sub']
            }
        except Exception as e:
            logger.error(f"Google Token Verification Failed: {e}")
            return None

auth_service = AuthService()