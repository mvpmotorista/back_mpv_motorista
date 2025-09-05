import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path
from sqlalchemy import and_, case, distinct, func, or_, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import aliased

from app.api.deps import AsyncSessionDep, CurrentUser, ResourceAccess
from app.enums.eumeradores import StatusEnum, TipoPerfilEnum

# from app.models.core import Documentos
# from app.models.perfis import Perfil
from app.users.models.users import User
from fastapi import Depends
from pydantic import BaseModel, ConfigDict, constr, Field
from sqlalchemy.ext.asyncio import AsyncSession

# from app.schemas.core import DocumentosOut
# from app.schemas.perfis import AlunoContratoOut, AlunoCreate, AlunoOut, AlunoPatch
# from app.service.aluno import email_cadastro_aluno
# from app.service.log_atividade import AcaoEnum

router = APIRouter(prefix="/perfil", tags=["perfil"])


class PerfilIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nome: str
    telefone: str
    genero: str | None = None


class PerfilOut(BaseModel):
    id: uuid.UUID
    nome: str
    telefone: str
    genero: str | None

    class Config:
        orm_mode = True


@router.put("/me", response_model=PerfilOut, summary="Atualiza perfil do usuário")
async def salvar_perfil(
    payload: PerfilIn,
    session: AsyncSession = Depends(AsyncSessionDep),
    current_user: User = Depends(CurrentUser),
):
    stmt = select(User).where(User.id == current_user.id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.nome = payload.nome
    user.telefone = payload.telefone
    user.genero = payload.genero

    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Erro ao salvar perfil")

    return user
