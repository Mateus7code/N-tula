from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.note import Note, NoteTag
from app.models.tag import Tag
from app.schemas.note import NoteOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=List[NoteOut])
def search_notes(
    q: str = Query(..., min_length=1, description="Termo de busca"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    term = f"%{q}%"
    notes = (
        db.query(Note)
        .options(joinedload(Note.note_tags).joinedload(NoteTag.tag), joinedload(Note.media))
        .filter(Note.user_id == current_user.id)
        .filter(
            or_(
                Note.title.ilike(term),
                Note.content.ilike(term),
                Note.note_tags.any(NoteTag.tag.has(Tag.name.ilike(term))),
            )
        )
        .order_by(Note.updated_at.desc())
        .all()
    )
    return notes
