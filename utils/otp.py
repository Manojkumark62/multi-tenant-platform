import secrets
from pwdlib import PasswordHash

otp_hash = PasswordHash.recommended()

def generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))

def hash_otp(otp: str) -> str:
    return otp_hash.hash(otp)

def verify_otp(otp: str, hashed_otp: str) -> bool:
    return otp_hash.verify(otp, hashed_otp)