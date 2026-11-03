import hashlib, os
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings

def hash_password(plain: str) -> str:
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", plain.encode(),salt.encode(), 100_000).hex()
    return f"{salt}${digest}"

def verify_password(plain: str, stored: str)-> bool:
    salt, digest = stored.split("$")
    return hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 100_000).hex() == digest

def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

