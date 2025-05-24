# services/auth_service/utils/security.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "super-secret"


def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=3)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY)
