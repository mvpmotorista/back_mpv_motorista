import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["static"])


@router.get("/{file_path:path}")
async def serve_static_file(file_path: str) -> Any:
    """
    Serve arquivos estáticos do diretório static.

    Args:
        file_path: Caminho do arquivo dentro do diretório static

    Returns:
        FileResponse: Arquivo solicitado

    Raises:
        HTTPException: 404 se o arquivo não for encontrado
    """
    # Caminho base para arquivos estáticos
    static_dir = Path("static")

    # Construir o caminho completo do arquivo
    full_path = static_dir / file_path

    # Verificar se o arquivo existe e está dentro do diretório static
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    # Verificar se o caminho não tenta sair do diretório static (segurança)
    try:
        full_path.resolve().relative_to(static_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Determinar o tipo de conteúdo baseado na extensão
    content_type = "application/octet-stream"
    if file_path.endswith(('.jpg', '.jpeg')):
        content_type = "image/jpeg"
    elif file_path.endswith('.png'):
        content_type = "image/png"
    elif file_path.endswith('.gif'):
        content_type = "image/gif"
    elif file_path.endswith('.svg'):
        content_type = "image/svg+xml"
    elif file_path.endswith('.css'):
        content_type = "text/css"
    elif file_path.endswith('.js'):
        content_type = "application/javascript"
    elif file_path.endswith('.html'):
        content_type = "text/html"
    elif file_path.endswith('.json'):
        content_type = "application/json"
    elif file_path.endswith('.pdf'):
        content_type = "application/pdf"
    elif file_path.endswith('.txt'):
        content_type = "text/plain"

    return FileResponse(path=str(full_path), media_type=content_type, filename=os.path.basename(file_path))
