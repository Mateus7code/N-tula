from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.note import Note, NoteTag
from app.models.tag import Tag
from app.schemas.note import NoteCreate, NoteUpdate, NoteOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])


def get_note_or_404(note_id: int, user_id: int, db: Session) -> Note:
    note = (
        db.query(Note)
        .options(joinedload(Note.note_tags).joinedload(NoteTag.tag), joinedload(Note.media))
        .filter(Note.id == note_id, Note.user_id == user_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    return note


def sync_tags(note: Note, tag_ids: List[int], user_id: int, db: Session):
    db.query(NoteTag).filter(NoteTag.note_id == note.id).delete()
    for tag_id in tag_ids:
        tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user_id).first()
        if tag:
            db.add(NoteTag(note_id=note.id, tag_id=tag.id))


@router.get("/", response_model=List[NoteOut])
def list_notes(
    tag_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Note)
        .options(joinedload(Note.note_tags).joinedload(NoteTag.tag), joinedload(Note.media))
        .filter(Note.user_id == current_user.id)
    )
    if tag_id:
        query = query.join(NoteTag).filter(NoteTag.tag_id == tag_id)
    return query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()


@router.post("/", response_model=NoteOut, status_code=201)
def create_note(
    data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = Note(user_id=current_user.id, title=data.title, content=data.content, is_pinned=data.is_pinned)
    db.add(note)
    db.commit()
    db.refresh(note)
    sync_tags(note, data.tag_ids, current_user.id, db)
    db.commit()
    return get_note_or_404(note.id, current_user.id, db)


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_note_or_404(note_id, current_user.id, db)


@router.patch("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int,
    data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note_or_404(note_id, current_user.id, db)
    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    if data.is_pinned is not None:
        note.is_pinned = data.is_pinned
    if data.tag_ids is not None:
        sync_tags(note, data.tag_ids, current_user.id, db)
    db.commit()
    return get_note_or_404(note_id, current_user.id, db)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = get_note_or_404(note_id, current_user.id, db)
    db.delete(note)
    db.commit()
