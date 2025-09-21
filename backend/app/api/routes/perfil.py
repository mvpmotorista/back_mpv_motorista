import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path
import jwt
from pydantic import BaseModel, ConfigDict, Field, constr
from sqlalchemy import and_, case, distinct, func, or_, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.api.deps import AsyncSessionDep, CurrentUser, ResourceAccess
from app.enums.eumeradores import StatusEnum, TipoPerfilEnum
from app.users.models.users import User

router = APIRouter(prefix="/perfil", tags=["perfil"])


class NewAcount(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nome: str
    telefone: str
    token: str
    genero: str | None = None


class PerfilOut(BaseModel):
    id: uuid.UUID
    nome: str
    telefone: str
    genero: str | None

    class Config:
        orm_mode = True




