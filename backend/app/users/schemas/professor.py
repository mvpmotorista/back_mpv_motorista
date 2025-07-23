from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, field_serializer, model_validator

from app.schemas.perfis import TipoAula
from app.service.supabase import url_builder


class DisponibilidadeEntrada(BaseModel):
    data_ini: datetime
    data_fim: datetime
    tipo: TipoAula
    comentario: str | None

    @model_validator(mode="after")
    def check_datas(self) -> 'DisponibilidadeEntrada':
        if self.data_fim < self.data_ini:
            raise ValueError("data_fim não pode ser menor que data_ini")
        return self


class DisponibilidadeEntradaEdicao(BaseModel):
    data_ini: datetime | None
    data_fim: datetime | None
    tipo: TipoAula | None
    comentario: str | None

    @model_validator(mode="after")
    def check_datas(self) -> 'DisponibilidadeEntradaEdicao':
        if (self.data_fim and self.data_fim) and not self.data_fim > self.data_ini:  # type: ignore
            raise ValueError("data_fim não pode ser menor que data_ini")
        return self


class DiaDisponibilidade(BaseModel):
    is_disponivel: bool


class IntervaloHorario(BaseModel):
    periodo: str
    intervalo_ini: time
    intervalo_fim: time
    seg: DiaDisponibilidade | None = None
    ter: DiaDisponibilidade | None = None
    qua: DiaDisponibilidade | None = None
    qui: DiaDisponibilidade | None = None
    sex: DiaDisponibilidade | None = None
    sab: DiaDisponibilidade | None = None
    dom: DiaDisponibilidade | None = None


class CalendarioData(BaseModel):
    calendario: list[IntervaloHorario]
    dia_seg: date
    dia_ter: date
    dia_qua: date
    dia_qui: date
    dia_sex: date
    dia_sab: date
    dia_dom: date
    dat_ini_prox_semana: date
    dat_ini_semana_anterior: date
    dat_ini_semana_anterior: date
    dat_fim_semana_anterior: date


class CalendarioResponse(BaseModel):
    data: CalendarioData


class PeriodoDisponibilidade(BaseModel):
    data: DiaDisponibilidade


class CalendarioResponse2(BaseModel):
    data: CalendarioData


class HorarioDisponivel(BaseModel):
    data_ini: datetime
    data_fim: datetime
    tipo: TipoAula
    comentario: str | None
    id: int | None


class HorarioDisponivelTodosProfessores(BaseModel):
    data_ini: datetime
    data_fim: datetime
    tipo: TipoAula


class ProfessorDisponibilidade(BaseModel):
    horarios: list[HorarioDisponivelTodosProfessores]
    nm_professor: str
    tipo: str
    foto: str | None = None

    @field_serializer("foto")
    def serialize_path(self, path: str) -> str:
        return url_builder(path)


class ListaHorario(BaseModel):
    data: list[HorarioDisponivel]


class FinanceiroProfessor(BaseModel):
    aulas_planejadas: int
    aulas_realizadas: int
    duracao_total_minutos: int = 0
    valor_hora: float = 0.0

    horas_trabalhadas: float = 0.0
    total_a_receber: float = 0.0

    @model_validator(mode='before')
    def calcular_campos_automaticamente(cls, values):
        duracao = values.get("duracao_total_minutos", 0)
        valor_hora = values.get("valor_hora", 0.0)

        values["horas_trabalhadas"] = round(duracao / 60, 2)
        values["total_a_receber"] = round(values["horas_trabalhadas"] * valor_hora, 2)
        return values
