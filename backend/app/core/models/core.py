from datetime import datetime
from sqlalchemy import Column, Boolean, ForeignKey, Integer, DateTime, String
from app.datetime_utils import get_utc_now
from app.database import Base  # Importando a base declarativa do SQLAlchemy


class Log(Base):
    __abstract__ = True  # Classe base, não cria tabela própria
    __table_args__ = {"schema": None}  # você pode definir um schema se quiser

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    deleted_by = Column(Integer, nullable=True)


# def soft_delete_values():
#     now = get_utc_now()
#     return {
#         "is_active": False,
#         "updated_at": now,
#         "deleted_at": now,
#     }


class VeiculoMotorista(Log):
    __tablename__ = "veiculos_motoristas"
    __table_args__ = {"schema": None}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    motorista_id = Column(Integer, ForeignKey("users.id", ondelete='SET NULL'))

    crlv = Column(String(1000), nullable=True)
    placa = Column(String(10), nullable=True)
    cor = Column(String(20), nullable=True)
    crlv_arquivo = Column(String(1000), nullable=True)
    foto_carro = Column(String(100), nullable=True)
