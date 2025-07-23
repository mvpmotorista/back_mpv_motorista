import calendar
import decimal
from datetime import date, datetime, time
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.service.supabase import url_builder


class TipoCurso(str, Enum):
    INTENSIVO = 'INTENSIVO'
    REGULAR = 'REGULAR'


class HorarioPreferenciaAluno(BaseModel):
    hora_ini: time
    hora_fim: time
    dia_semana: calendar.Day


class DataEspecifica(BaseModel):
    dat_ini: datetime
    dat_fim: datetime


class ProfessorQtdAula(BaseModel):
    hash: UUID
    qtd_aula: int|None


class ContratoBase(BaseModel):
    aluno_hash: UUID
    tipo_curso: TipoCurso
    # Número de aulas semanais contratadas pelo aluno (deve ser maior que 0)
    numero_aulas_semanais: int = Field(
        gt=0, description="Número de aulas semanais contratadas pelo aluno (deve ser maior que 0)"
    )
    duracao_aula_minutos: int = Field(gt=0, description="Duration of each class in minutes")
    valor_hora_aula: decimal.Decimal = Field(
        gt=0, description="Valor da hora/aula em reais (BRL), use ponto como separador decimal. Exemplo: 75.50"
    )
    local_aula: str | None = None
    data_inicio: date
    data_termino: date
    professores_hash: list[ProfessorQtdAula] = Field(default_factory=list)
    preferencia_semanal: list[HorarioPreferenciaAluno] | None = None
    data_especifica: list[DataEspecifica] | None = None
    tipo_disponibilidade: int | None


class ContratoUpdate(BaseModel):
    aluno_hash: UUID | None = None
    tipo_curso: TipoCurso | None = None
    numero_aulas_semanais: int | None = Field(gt=0)
    duracao_aula_minutos: int | None = Field(gt=0)
    valor_hora_aula: decimal.Decimal | None = Field(gt=0)
    local_aula: str | None = None
    data_inicio: date | None = None
    data_termino: date | None = None
    professores_hash: list[ProfessorQtdAula] | None = Field(default_factory=list)
    preferencia_semanal: list[HorarioPreferenciaAluno] | None = None
    data_especifica: DataEspecifica | None = None
    tipo_disponibilidade: int | None


class ContratoCustoIn(BaseModel):
    valor: decimal.Decimal
    tipo: str
    descricao: str | None = None


class ContratoCustoOut(ContratoCustoIn): ...


class ContratoCreate(ContratoBase):
    status: str = 'ativo'
    custos: list[ContratoCustoIn] | None = Field(default_factory=list)


class ContratoOut(ContratoBase):
    id: int
    custos: list[ContratoCustoOut] = Field(default_factory=list)

    class Config:
        orm_mode = True


class Contratos(BaseModel):
    data: list[dict] = Field(default_factory=list)


class Options(BaseModel):
    nome: str
    hash: UUID
    foto: str | None

    @field_serializer("foto")
    def serialize_path(self, path: str) -> str:
        return url_builder(path)
