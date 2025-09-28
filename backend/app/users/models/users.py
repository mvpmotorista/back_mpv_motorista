from datetime import date
from typing import Optional
import uuid

from geoalchemy2 import Geometry
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
# supondo que você tenha convertido Log para SQLAlchemy

from datetime import date
from sqlalchemy import Column, Index, Integer, String, Boolean, Date
from geoalchemy2 import Geometry
from app.core.models.core import Log
from app.datetime_utils import get_utc_now
from app.database import Base
from pydantic import BaseModel


# Generic message
class Message(BaseModel):
    message: str


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: str | None = None


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class UserBase(BaseModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    role: str | None = Field(max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


# supondo que você tenha convertido Log para SQLAlchemy


class User(Log, Base):
    __tablename__ = "users"
    # ou "public", se quiser

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(255), default="user", nullable=True)
    genero = Column(String(10), nullable=True)
    telefone = Column(String(30), nullable=True)
    data_nascimento = Column(Date, nullable=True)
    is_available = Column(Boolean, default=True, nullable=True)
    current_location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    veiculo_id = Column(Integer, nullable=True)  # foreign key se precisar
    status_corrida = Column(String(50), nullable=True)
    cpf = Column(String(14), nullable=True)
    cnh = Column(String(20), nullable=True)
    cnh_arquivo = Column(String(1000), nullable=True)
    registry_completed = Column(Boolean, default=False, nullable=True)
    registry_approved = Column(Boolean, default=False, nullable=True)

    # Endereço

    logradouro = Column(String(100), nullable=True)
    numero = Column(String(10), nullable=True)
    complemento = Column(String(50), nullable=True)
    bairro = Column(String(50), nullable=True)
    cep = Column(String(10), nullable=True)
    cidade = Column(String(50), nullable=True)
    estado = Column(String(2), nullable=True)
    __table_args__ = ({"schema": None},)
    # foto_rosto = Column(String(1000), nullable=True)
