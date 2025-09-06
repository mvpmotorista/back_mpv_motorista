import decimal
import uuid
from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from app.core.models.core import Log


class Perfil(Log, table=True):
    __tablename__: str = "perfis"  # type: ignore
    id: int = Field(primary_key=True)
    nome: str = Field(max_length=500)
    cpf: str | None = Field(default=None, max_length=11)
    foto: str | None = Field(default=None, max_length=255)
    tipo: str = Field(max_length=50)
    genero: str = Field(max_length=10)
    hash: UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)
    status_id: str | None = Field(foreign_key="status.id")
    email: EmailStr | None
    token: str | None = Field(max_length=20)
    telefone: str | None = Field(default=None, max_length=30)
    data_nascimento: date | None = Field(default=None)

class Endereco(Log, table=True):
    __tablename__: str = "enderecos"  # type: ignore
    id: int = Field(primary_key=True)
    perfil_id: int = Field(foreign_key="perfis.id")
    # perfil: Perfil = Relationship(back_populates="enderecos")
    logradouro: str | None = Field(default=None, max_length=100)
    numero: str | None = Field(default=None, max_length=10)
    complemento: str | None = Field(default=None, max_length=50)
    bairro: str | None = Field(default=None, max_length=50)
    cep: str | None = Field(default=None, max_length=10)
    cidade: str | None = Field(default=None, max_length=50)
    estado: str | None = Field(default=None, max_length=2)
