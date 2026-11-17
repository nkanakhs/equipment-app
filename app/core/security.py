from datetime import datetime
import os
import hmac
import hashlib
import base64
from app.core.config import settings

SESSION_COOKIE_NAME = "elm_session"
SESSION_DAYS = settings.session_days
PBKDF2_ITERATIONS = 260000


def _utc_now():
    return datetime.utcnow()


def hash_password(password: str) -> str:
    password = password or ""
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return (
        "pbkdf2_sha256$"
        + str(PBKDF2_ITERATIONS)
        + "$"
        + base64.b64encode(salt).decode("ascii")
        + "$"
        + base64.b64encode(derived).decode("ascii")
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        (algorithm, iterations, salt_b64, hash_b64) = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        actual = hashlib.pbkdf2_hmac(
            "sha256", (password or "").encode("utf-8"), salt, int(iterations)
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def session_token_hash(token: str) -> str:
    return hashlib.sha256((token or "").encode("utf-8")).hexdigest()
