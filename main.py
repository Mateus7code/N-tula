from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine
from app.models import User, Note, NoteTag, Tag, Media
from app.routers import auth, notes, tags, media, search

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nótula API",
    description="API do gerenciador de anotações Nótula",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(tags.router)
app.include_router(media.router)
app.include_router(search.router)


@app.get("/")
def root():
    return {"message": "Nótula API está rodando 🚀", "docs": "/docs"}
