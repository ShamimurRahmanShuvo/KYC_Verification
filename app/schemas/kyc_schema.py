from pydantic import BaseModel
from typing import Optional


class AdminReviewRequest(BaseModel):
    action: str
    reviewer: str
    notes: Optional[str] = None


class StatusResponse(BaseModel):
    id: int
    status: str
    verified: bool
