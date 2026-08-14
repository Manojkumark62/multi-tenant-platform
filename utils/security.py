from secrets import token_urlsafe

def generate_secure_token(length: int = 32) -> str:
    return token_urlsafe(length)