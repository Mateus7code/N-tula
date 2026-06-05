from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.tag import TagOut
from app.schemas.media import MediaOut


class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    is_pinned: bool = False
    tag_ids: List[int] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    tag_ids: Optional[List[int]] = None


class NoteOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    tags: List[TagOut] = []
    media: List[MediaOut] = []

    model_config = {"from_attributes": True}
