from sqlmodel import Field, Relationship
from app.core.models.core import Log


class Corrida(Log, table=True):
    __tablename__: str = "corridas"  # type: ignore
    id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': True})
    # passageiro
    # motorista
    # origem=
    # destino=
    # preco=
    # placa=
    # veiculo_cp
    # forma_pagamento





