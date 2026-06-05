from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.note import Note
from app.models.media import Media
from app.schemas.media import MediaOut
from app.dependencies import get_current_user
from app.services.storage import save_upload, delete_upload

router = APIRouter(prefix="/notes/{note_id}/media", tags=["media"])


@router.post("/", response_model=MediaOut, status_code=201)
async def upload_media(
    note_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    saved = await save_upload(file)

    media = Media(
        note_id=note_id,
        filename=saved["filename"],
        url=saved["url"],
        mime_type=saved["mime_type"],
        size_bytes=saved["size_bytes"],
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


@router.delete("/{media_id}", status_code=204)
def delete_media(
    note_id: int,
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    media = db.query(Media).filter(Media.id == media_id, Media.note_id == note_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Mídia não encontrada")

    delete_upload(media.filename)
    db.delete(media)
    db.commit()
