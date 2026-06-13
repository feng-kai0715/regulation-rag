from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    source: Optional[str] = None
    duration: Optional[float] = None