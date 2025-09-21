import asyncio
import uuid
from datetime import date, datetime
from typing import Any, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_serializer
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    AsyncSessionDep,
    CurrentUser,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.users.models.users import (
    User,
)

# from app.schemas.perfis import PerfilMe
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/driver", tags=["driver"])


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    genero: Optional[str] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None
    cnh: Optional[str] = None
    cnh_arquivo: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None


class UserCreate(UserBase): ...


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool


class NewAcount(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    token: str


@router.post("/account-status")
async def account_status(payload: NewAcount, session: AsyncSessionDep):
    token = jwt.decode(payload.token, options={"verify_signature": False})
    email = token['email'].lower()
    result = await session.execute(select(User).where(User.email == email))
    db_user = result.scalars().first()
    if db_user:
        return {'registry_completed': db_user.registry_completed, 'registry_approved': db_user.registry_approved}
    else:
        new_user = User(email=email, hashed_password='dsdsdsds', full_name='cadastro imcompleto', role='driver')
        session.add(new_user)
        await session.commit()
        return {'registry_completed': False, 'registry_approved': False}


@router.post("", response_model=UserRead)
async def create_driver(user_in: UserCreate, session: AsyncSessionDep):
    # verificar se já existe
    # token = jwt.decode(dados.token, options={"verify_signature": False})
    result = await session.execute(select(User).where(User.email == user_in.email))
    db_user = result.scalars().first()
    if db_user:
        if 'driver' == db_user.role:
            raise HTTPException(status_code=400, detail="Email já registrado")
        else:
            db_user.role = 'driver'
            db_user.full_name = user_in.full_name
            db_user.genero = user_in.genero
            db_user.telefone = user_in.telefone
            db_user.data_nascimento = user_in.data_nascimento
            db_user.cpf = user_in.cpf
            db_user.cnh = user_in.cnh
            db_user.cnh_arquivo = user_in.cnh_arquivo
            db_user.logradouro = user_in.logradouro
            db_user.numero = user_in.numero
            db_user.complemento = user_in.complemento
            db_user.bairro = user_in.bairro
            db_user.cep = user_in.cep
            db_user.cidade = user_in.cidade
            db_user.estado = 'pr'
            await session.commit()
            await session.refresh(db_user)
            return db_user
    # criar novo user
    new_user = User(
        email=user_in.email,
        hashed_password='dsdsdsds',
        full_name=user_in.full_name,
        role='driver',
        genero=user_in.genero,
        telefone=user_in.telefone,
        data_nascimento=user_in.data_nascimento,
        cpf=user_in.cpf,
        cnh=user_in.cnh,
        cnh_arquivo=user_in.cnh_arquivo,
        logradouro=user_in.logradouro,
        numero=user_in.numero,
        complemento=user_in.complemento,
        bairro=user_in.bairro,
        cep=user_in.cep,
        cidade=user_in.cidade,
        estado='pr',
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
