from datetime import datetime
from sqlalchemy import Column, Boolean, Integer, DateTime
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



# class Municipio(Log, table=True):
#     __tablename__: str = "municipios"  # type: ignore
#     id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
#     nome: str
#     uf: str = Field(max_length=2)


# class Feriado(Log, table=True):
#     __tablename__: str = "feriados"  # type: ignore
#     id: int = Field(default=None, primary_key=True)
#     data: date = Field(nullable=False)
#     abrangencia: str = Field(max_length=50)
#     municipio_id: int | None = Field(default=None, foreign_key="municipios.id")
#     descricao: str | None = Field(default=None, max_length=500)
#     uf: str | None = Field(default=None, max_length=2)


# class LogAtividade(Log, table=True):
#     __tablename__: str = "log_atividade"  # type: ignore
#     id: int | None = Field(default=None, primary_key=True)
#     # perfil_id: int = Field(foreign_key="perfis.id", nullable=False)
#     acao: str = Field(nullable=False, max_length=255)
#     detalhe: str = Field(nullable=False, max_length=500)


# def soft_delete_values():
#     now = get_utc_now()
#     return {
#         "is_active": False,
#         "updated_at": now,
#         "deleted_at": now,
#     }


# class VeiculoBase(Log, table=True):
#     __tablename__: str = "veiculos_base"  # type: ignore
#     id: int = Field(primary_key=True)

#     # Categoria do veículo
#     categoria: str | None = Field(default=None, max_length=50)  # Categoria conforme etiquetagem

#     # Informações básicas do veículo
#     marca: str = Field(max_length=100, nullable=False)
#     modelo: str = Field(max_length=100, nullable=False)
#     motor: str = Field(max_length=50, nullable=True)
#     versao: str | None = Field(default=None, max_length=100)

#     # Transmissão - conforme etiquetagem (M, A, DCT, MTA, CVT)
#     transmissao_tipo: str | None = Field(default=None, max_length=10)  # M, A, DCT, MTA, CVT
#     transmissao_velocidades: int | None = Field(default=None)  # Número de velocidades

#     # Ar condicionado
#     ar_condicionado: bool | None = Field(default=None)

#     # Direção assistida - conforme etiquetagem (H, M, E, E-H)
#     direcao_tipo: str | None = Field(default=None, max_length=10)  # H, M, E, E-H

#     # Combustível - conforme etiquetagem (E, G, F)
#     combustivel_tipo: str | None = Field(default=None, max_length=10)  # E, G, F

#     # Emissões no escapamento - Poluentes
#     emissoes_nmhc: float | None = Field(default=None)  # NMHC (g/km)
#     emissoes_co: float | None = Field(default=None)  # CO (g/km)
#     emissoes_nox: float | None = Field(default=None)  # NOx (g/km)
#     reducao_relativa_limite: float | None = Field(default=None)  # Redução relativa ao limite

#     # Emissões no escapamento - Gás Efeito Estufa
#     co2_fossil_etanol: float | None = Field(default=None)  # CO2 fóssil etanol (g/km)
#     co2_fossil_gasolina: float | None = Field(default=None)  # CO2 fóssil gasolina (g/km)

#     # Quilometragem por litro - Etanol
#     km_l_etanol_cidade: float | None = Field(default=None)  # Etanol cidade (km/l)
#     km_l_etanol_estrada: float | None = Field(default=None)  # Etanol estrada (km/l)

#     # Quilometragem por litro - Gasolina
#     km_l_gasolina_cidade: float | None = Field(default=None)  # Gasolina cidade (km/l)
#     km_l_gasolina_estrada: float | None = Field(default=None)  # Gasolina estrada (km/l)

#     # Consumo energético
#     consumo_energetico: float | None = Field(default=None)  # MJ/km

#     # Classificação PBE
#     classificacao_pbe_relativa: str | None = Field(default=None, max_length=20)  # Comparação relativa na categoria
#     classificacao_pbe_absoluta: str | None = Field(default=None, max_length=20)  # Comparação absoluta geral

#     # Selo CONPET de Eficiência Energética
#     selo_conpet: bool | None = Field(default=None)

#     # Campos legados (mantidos para compatibilidade)
#     quantidade_portas: int = Field(default=4, nullable=True)
#     # Categoria do veículo
#     categoria_externa: str | None = Field(default=None, max_length=50)
#     categoria_interna: str | None = Field(default=None, max_length=50)


# class VeiculoMotorista(Log, table=True):
#     __tablename__: str = "veiculos_motoristas"
#     __table_args__ = {"schema": "public"}
#       # type: ignore
#     id: int = Field(primary_key=True)
#     motorista_id: int = Field(foreign_key="user.id", primary_key=True)
#     crlv: str | None = Field(default=None, max_length=1000)
#     # crlv_arquivo: str | None = Field(default=None, max_length=1000)
#     # foto_carro: str | None = Field(default=None, max_length=100)
#     placa: str | None = Field(default=None, max_length=10)
#     cor: str | None = Field(default=None, max_length=20)
