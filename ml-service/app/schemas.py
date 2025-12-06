from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException
from typing import List


class SearchResult(BaseModel):
    sentence: str
    file_name: str
    position: int
    score: float

class SearchResponse(BaseModel):
    status: str = "success"
    results: List[SearchResult]

class SuccessResponse(BaseModel):
    status: str = "success"
    file_name: Optional[str] = None
    sentences_added: Optional[int] = None
    max_id: Optional[int] = None

    @property
    def status_code(self) -> int:
        return 200
    class Config:
        orm_mode = True

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_type: Optional[str] = None

    @property
    def status_code(self) -> int:
        if self.error_type == "validation":
            return 400
        elif self.error_type == "file_error":
            return 400
        elif self.error_type == "processing":
            return 422
        elif self.error_type == "system":
            return 500
        else:
            return 500

    def to_http_exception(self):
        """Convert this error to an HTTPException and raise it"""
        raise HTTPException(
            status_code=self.status_code,
            detail=self.message
        )

def handle_response(response):
    if isinstance(response, ErrorResponse):
        response.to_http_exception()
    return response.dict()
