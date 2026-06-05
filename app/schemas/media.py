from pydantic import BaseModel
from datetime import datetime


class MediaOut(BaseModel):
    id: int
    filename: str
    url: str
    mime_type: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}
