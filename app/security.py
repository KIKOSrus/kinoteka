"""Хеширование паролей и JWT-токены."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, SECRET_KEY


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: int, role: str) -> tuple[str, int]:
    """Возвращает (токен, время жизни в секундах)."""
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "role": role, "iat": now, "exp": now + expires}
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, int(expires.total_seconds())


def decode_access_token(token: str) -> dict:
    """Бросает jwt.PyJWTError, если токен неверный или просрочен."""
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
