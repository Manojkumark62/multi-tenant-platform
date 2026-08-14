from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

def get_pagination_offset(page: int, page_size: int) -> int:
    return (page - 1) * page_size

def get_total_pages(total_items: int, page_size: int) -> int:
    return (total_items + page_size - 1) // page_size