import os
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.params import Form
from pydantic import BaseModel, Field, HttpUrl, computed_field, field_serializer
from sqlalchemy import delete, desc, exists, func, select

from app.api.deps import AsyncSessionDep, CurrentUser, ResourceAccess
from app.core.permissions import Role
# from app.models.core import Documentos
# from app.models.perfis import Perfil
# from app.service.supabase import SupabaseStorageService, url_builder
# from app.service.upload import S3Service


class Link(BaseModel):  # type: ignore
    id: int | None
    title: str | None
    ícone: str | None
    url: str | None


router = APIRouter(prefix="/core", tags=["core"])


class LinkImage(BaseModel):
    filename: str
    url: HttpUrl
    path: str


class DocumentosIn(BaseModel):
    filename: str
    url: HttpUrl
    path: str
    descricao: str | None = None


class DocumentosOut(BaseModel):
    id: int
    nome: str
    descricao: str | None = None
    path: str = Field(..., exclude=True)  # usado internamente, mas omitido no dump

    @computed_field
    @property
    def url(self) -> HttpUrl:
        return url_builder(self.path)


@router.post("/upload-image", response_model=LinkImage)
async def upload_image(current_user: CurrentUser, file: UploadFile = File(...)):
    extension = os.path.splitext(file.filename)[1]
    filename = str(uuid4()) + extension
    resultado = SupabaseStorageService().upload_fileobj(file, filename, file.content_type)
    link = LinkImage(filename=filename, url=resultado['url'], path=resultado['path'])
    return link


@router.post("/documentos")
async def upload_documentos(
    session: AsyncSessionDep,
    current_user: CurrentUser,
    hash: UUID = Form(...),
    file: UploadFile = File(...),
    _=ResourceAccess('documentos'),
):
    try:
        extension = os.path.splitext(file.filename)[1].lstrip('.')
    except:
        extension = None
    nome_base = os.path.splitext(file.filename)[0]

    stmt_exists = select(
        exists().where(
            Documentos.nome_base == nome_base, Documentos.extesao == extension, Documentos.is_active == True
        )
    )
    result = await session.execute(stmt_exists)
    if result.scalar_one_or_none():
        stmt = select(Documentos.nome_base).where(
            Documentos.nome_base.like(f"{nome_base}%"),
            Documentos.extesao == extension,
            Documentos.is_active == True,
        )
        result = await session.execute(stmt)

        ls_documento = set(result.scalars().all())
        if ls_documento:
            for i in range(1, 1000):
                novo_base = f"{nome_base}_{i}"
                nova_versao = i
                if novo_base not in ls_documento:
                    break
            nome_final = f"{novo_base}.{extension}"
            nome_storage = nome_final
        else:
            nova_versao = 1
            novo_base = nome_base
            nome_final = f"{nome_base}.{extension}"
            nome_storage = nome_final
    else:
        nova_versao = 1
        novo_base = nome_base
        nome_final = f"{nome_base}.{extension}"
        nome_storage = nome_final

    resultado = SupabaseStorageService().upload_fileobj(file, nome_storage, file.content_type)

    if not resultado:
        raise HTTPException(status_code=500, detail="Erro ao fazer upload do arquivo")

    if 'key' not in resultado or 'url' not in resultado or 'path' not in resultado:
        raise HTTPException(status_code=500, detail="Erro ao processar o arquivo")
    result = await session.execute(select(Perfil.id).where(Perfil.hash == hash))

    d = Documentos(
        owner_id=result.scalar_one(),
        nome_base=novo_base,
        path=resultado['path'],
        descricao=None,
        versao=nova_versao,
        nome_final=nome_final,
        extesao=extension if extension else None,
    )
    session.add(d)
    await session.commit()
    link = LinkImage(filename=nome_final, url=resultado['url'], path=resultado['path'])
    return link


@router.get("/documentos/{hash}")
async def get_documentos(
    current_user: CurrentUser,
    session: AsyncSessionDep,
    _=ResourceAccess('documentos'),
):
    result = await session.execute(
        select(Documentos.id, Documentos.nome, Documentos.path, Documentos.descricao).where(
            Documentos.is_active == True
        )
    )
    return [DocumentosOut(**row) for row in result.mappings().all]


@router.delete("/documentos/{id}")
async def delete_documento(
    id: int,
    current_user: CurrentUser,
    session: AsyncSessionDep,
    _=ResourceAccess('documentos'),
):
    await session.execute(delete(Documentos).where(Documentos.id == id))
    await session.commit()
    return {"detail": "Documento deletado com sucesso"}
