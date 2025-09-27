from datetime import date
import io
from typing import Optional
from uuid import uuid4
import jwt
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlmodel import select

from app.api.deps import (
    AsyncSessionDep,
    CurrentUser,
)
from app.core.models.core import VeiculoMotorista
from app.services import leitor_crlv
from app.services.supabase import SupabaseStorageService
from app.users.models.users import (
    User,
)

# from app.schemas.perfis import PerfilMe


router = APIRouter(prefix="/driver", tags=["driver"])


class UserBase(BaseModel):
    email: EmailStr
    foto_rosto: Optional[str] = None
    full_name: Optional[str] = None
    genero: Optional[str] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None
    cnh_arquivo: Optional[str] = None
    cnh_arquivo_verso: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    path: Optional[str] = None


class DriverIn(UserBase): ...


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool


class Vehicle(BaseModel):
    crlv_arquivo: str


class DriverRegister(BaseModel):
    user: DriverIn
    veiculo_motorista: Vehicle


class NewAcount(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    token: str


class CRLVe(BaseModel):
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
        # new_user = User(email=email, hashed_password='dsdsdsds', full_name='cadastro imcompleto', role='driver')
        # session.add(new_user)
        # await session.commit()
        return {'registry_completed': False, 'registry_approved': False}


@router.get(
    "/me",
    response_model=UserRead,
)
async def user_info(
    session: AsyncSessionDep,
    current_user: CurrentUser,
):
    return current_user


@router.post("", response_model=UserRead)
async def create_driver(dados: DriverRegister, session: AsyncSessionDep):  # verificar se já existe
    new_user = User(
        email=dados.user.email,
        full_name=dados.user.full_name,
        role='driver',
        hashed_password='dsdsdsds',  # gerar senha aleatória e enviar por email
        genero=dados.user.genero,
        telefone=dados.user.telefone,
        data_nascimento=dados.user.data_nascimento,
        cpf=dados.user.cpf,
        # cnh=user_in.cnh,
        cnh_arquivo=dados.user.cnh_arquivo,
        logradouro=dados.user.logradouro,
        numero=dados.user.numero,
        complemento=dados.user.complemento,
        bairro=dados.user.bairro,
        cep=dados.user.cep,
        cidade=dados.user.cidade,
        estado='pr',
    )
    session.add(new_user)
    await session.flush()
    await session.refresh(new_user)
    file = SupabaseStorageService().dowload_file(dados.veiculo_motorista.crlv_arquivo)
    text = leitor_crlv.cast_pdf_to_text(io.BytesIO(file))
    vehicle_parsed = leitor_crlv.parse_crlv_text(text)
    vehicle = VeiculoMotorista(
        placa=vehicle_parsed.veiculo.placa,
        cor=vehicle_parsed.veiculo.cor,
        motorista_id=new_user.id,
    )
    session.add(vehicle)
    await session.commit()
    return new_user


class UploadCRLVRequest(BaseModel):
    path: str


@router.post("/register_vehicle")
async def register_vehicle(
    payload: UploadCRLVRequest,
    session: AsyncSessionDep,  # se for via Depends, ajuste: session: AsyncSessionDep
):
    filename = payload.path

    await session.commit()
    return {"status": "ok"}


@router.post("/upload")
async def upload_pdf(session: AsyncSessionDep, file: UploadFile = File(...)):
    filename = str(uuid4()) + '_' + file.filename
    resultado = SupabaseStorageService().upload_fileobj(file, filename, file.content_type)
    return resultado
