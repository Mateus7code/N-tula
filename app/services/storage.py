import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.core.config import settings

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# Configura o Cloudinary uma vez ao importar o módulo
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,  # sempre HTTPS
)


async def save_upload(file: UploadFile) -> dict:
    """Faz upload de uma imagem para o Cloudinary e retorna os metadados."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo de arquivo não permitido. Use JPG, PNG, GIF ou WEBP.",
        )

    content = await file.read()
    size = len(content)

    if size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo muito grande. Máximo: {settings.MAX_FILE_SIZE_MB}MB",
        )

    try:
        result = cloudinary.uploader.upload(
            content,
            folder=settings.CLOUDINARY_FOLDER,
            resource_type="image",
            # Gera automaticamente versões otimizadas
            eager=[{"quality": "auto", "fetch_format": "auto"}],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload: {str(e)}")

    return {
        "filename": result["public_id"],   # ID único no Cloudinary
        "url": result["secure_url"],       # URL HTTPS pública
        "mime_type": file.content_type,
        "size_bytes": size,
    }


def delete_upload(filename: str):
    """Remove uma imagem do Cloudinary pelo public_id."""
    try:
        cloudinary.uploader.destroy(filename)
    except Exception:
        pass  # Se falhar, não bloqueia a exclusão no banco
