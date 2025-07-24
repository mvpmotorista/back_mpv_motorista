from datetime import date, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.datetime_utils import get_utc_now


class Log(SQLModel):
    is_active: bool = True
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime | None
    deleted_at: datetime | None
    created_by: int | None
    updated_by: int | None
    deleted_by: int | None
    __table_args__ = {
        "schema": None
    }


class Status(Log, table=True):
    __tablename__: str = "status"  # type: ignore
    id: str | None = Field(default=None, primary_key=True)
    nome: str | None
    perfis: list["Perfil"] = Relationship(back_populates="status")


class Municipio(Log, table=True):
    __tablename__: str = "municipios"  # type: ignore
    id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
    nome: str
    uf: str = Field(max_length=2)


class Feriado(Log, table=True):
    __tablename__: str = "feriados"  # type: ignore
    id: int = Field(default=None, primary_key=True)
    data: date = Field(nullable=False)
    abrangencia: str = Field(max_length=50)
    municipio_id: int | None = Field(default=None, foreign_key="municipios.id")
    descricao: str | None = Field(default=None, max_length=500)
    uf: str | None = Field(default=None, max_length=2)


class LogAtividade(Log, table=True):
    __tablename__: str = "log_atividade"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    perfil_id: int = Field(foreign_key="perfis.id", nullable=False)
    acao: str = Field(nullable=False, max_length=255)
    detalhe: str = Field(nullable=False, max_length=500)


def soft_delete_values():
    now = get_utc_now()
    return {
        "is_active": False,
        "updated_at": now,
        "deleted_at": now,
    }
