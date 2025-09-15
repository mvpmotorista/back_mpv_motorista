from sqlmodel import Field, Relationship
from app.core.models.core import Log


class VeiculoMotorista(Log, table=True):
    __tablename__: str = "veiculos_motoristas"  # type: ignore
    id: int = Field(primary_key=True)
    placa: str = Field(index=True, max_length=20, unique=True)
    cor: str = Field(max_length=50)
    # motorista_id: int | None = Field(default=None, foreign_key="users.id")



