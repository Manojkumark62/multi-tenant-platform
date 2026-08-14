from time import monotonic
from fastapi import HTTPException, Request, status

_rate_limit_store: dict[str, list[float]] = {}

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    async def rate_limit_dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{request.url.path}:{client_ip}"
        current_time = monotonic()
        request_times = _rate_limit_store.get(key, [])
        request_times = [timestamp for timestamp in request_times if current_time - timestamp < window_seconds]

        if len(request_times) >= max_requests:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")

        request_times.append(current_time)
        _rate_limit_store[key] = request_times

    return rate_limit_dependency