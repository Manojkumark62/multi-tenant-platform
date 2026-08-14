import hashlib
import json

def generate_request_hash(payload: dict) -> str:
    normalized_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized_payload.encode("utf-8")).hexdigest()

def validate_idempotency_key(key: str) -> bool:
    return bool(key and len(key) <= 255)

def idempotency_key_matches(stored_hash: str, request_hash: str) -> bool:
    return stored_hash == request_hash