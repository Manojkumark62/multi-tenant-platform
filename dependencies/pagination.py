from fastapi import Query

def get_pagination(page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100)) -> dict:
    return {"page": page, "page_size": page_size, "offset": (page - 1) * page_size}