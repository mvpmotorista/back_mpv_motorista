import decimal
from datetime import date
from enum import Enum
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, condecimal, field_serializer

from app.enums.eumeradores import StatusEnum
from app.schemas.core import ColorHex, DocumentosOut
from app.schemas.cpf import CPFField
from app.service.supabase import url_builder


class AlunoCreate(BaseModel):
    nome: str
    foto: str | None = None
    email: EmailStr | None = None
    cor: str | None = None
    telefone: str | None = None
    cidade: str | None = None
    email_secundario: str | None = None
    telefone_secundario: str | None = None
    arquivo: str | None = None


class AlunoPatch(BaseModel):
    nome: str | None = None
    foto: str | None = None
    email: EmailStr | None = None
    cor: str | None = None
    telefone: str | None = None
    cidade: str | None = None
    email_secundario: str | None = None
    telefone_secundario: str | None = None
    arquivo: str | None = None


class AlunoOut(AlunoCreate):
    hash: UUID | None = None
    status: StatusEnum | None = None

    @field_serializer("foto")
    def serialize_path(self, path: str) -> str:
        return url_builder(path)

    @field_serializer("arquivo")
    def serialize_path(self, path: str) -> str:
        return url_builder(path)


class AlunoContratoOut(BaseModel):
    nome: str
    foto: Optional[str] = None
    hash: UUID
    email: Optional[EmailStr] = None
    cor: Optional[str] = None
    telefone: Optional[str] = None
    email_secundario: Optional[str] = None
    telefone_secundario: Optional[str] = None
    arquivo: Optional[str] = None
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    numero_aulas_semanais: Optional[int] = None
    status_contrato: Optional[str] = None
    tipo_curso: Optional[str] = None
    cidade: Optional[str] = None
    documentos: list[DocumentosOut] = Field(default_factory=list)
    professores: Optional[list[str]] = None  # Lista de nomes dos professores

    @field_serializer("foto")
    def serialize_path(self, path: str) -> str:
        return url_builder(path)


class TipoAula(str, Enum):
    online = "online"
    presencial = "presencial"
    ambos = "ambos"


class PerfilBase(BaseModel):
    carga_horaria_semanal: int | None = None
    valor_hora: decimal.Decimal | None = None
    nome: str = Field(max_length=500)
    cpf: str | None = Field(default=None, max_length=11)
    foto: str | None = Field(default=None, max_length=255)
    tipo: str = Field(max_length=50)
    tipo_aula: str | None = Field(default=None, max_length=20)
    status_id: str | None = None
    email: EmailStr
    cor: str | None = Field(default=None, max_length=20)
    municipio_id: int|None


class ProfessorCreate(BaseModel):
    nome: str
    cpf: CPFField
    foto: str | None = None
    carga_horaria_semanal: int | None = None
    tipo_aula: TipoAula
    valor_hora: Optional[condecimal(gt=0, decimal_places=2)] = None
    email: EmailStr
    cor: ColorHex | None
    status: StatusEnum = Field(..., alias="status_id")
    municipio_id: int
    model_config = {
        "populate_by_name": True,
    }


class PerfilAdminCreate(BaseModel):
    nome: str


class AlunoRead(BaseModel):
    nome: str
    foto: str | None
    email: str | None = None
    hash: UUID | None
    status: str | None

    @field_serializer("foto")
    def serialize_path(self, path: str) -> str:
        return url_builder(path)


class PerfilMe(BaseModel):
    nome: str
    foto: str | None
    email: str | None = None
    hash: UUID | None
    status: str | None
    tipo: str | None
    cor: str | None
    tipo_aula: str | None

    @field_serializer("foto")
    def serialize_path(self, path: str) -> str:
        return url_builder(path)


class ProfessorRead(BaseModel):
    nome: str
    foto: str | None
    email: str | None = None
    hash: UUID | None
    status: str | None
    cor: str | None
    valor_hora: decimal.Decimal | None
    tipo_aula: str | None = None
    cpf: Optional[CPFField] = None
    municipio_id: int|None
    documentos: list[DocumentosOut]|None = None

    @field_serializer("foto")
    def serialize_path(self, path: str) -> str:
        return url_builder(path)


class ProfessorPatch(BaseModel):
    nome: str = None
    cpf: Optional[CPFField] = None
    foto: Optional[str] = None
    carga_horaria_semanal: Optional[int] = None
    tipo_aula: Optional[TipoAula] = None
    valor_hora: Optional[condecimal(gt=0, decimal_places=2)] = None
    email: EmailStr | None = None
    status: StatusEnum | None
    cor: ColorHex | None
    municipio_id: int | None = None


class ResetSenha(BaseModel):
    token: str
    senha: str


class TrocarSenha(BaseModel):
    email: EmailStr
    senha: str
    token: str


class EmailRequest(BaseModel):
    email: EmailStr
