import re

def validate_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"^\+?[1-9]\d{7,14}$", phone))

def validate_slug(slug: str) -> bool:
    return bool(re.fullmatch(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))

def validate_uuid(value: str) -> bool:
    return bool(re.fullmatch(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$", value))