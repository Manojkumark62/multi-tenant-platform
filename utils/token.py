import hashlib
import secrets

def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generate_jti() -> str:
    return secrets.token_urlsafe(32)