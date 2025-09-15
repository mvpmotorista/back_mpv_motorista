from sqlmodel import Field, Relationship
from app.core.models.core import Log


class CategoriaCorrida(Log, table=True):
    __tablename__: str = "categorias_corridas"  # type: ignore
    id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
    nome: str = Field(max_length=100, nullable=False)
    descricao: str | None = Field(default=None, max_length=255)
    icone: str | None = Field(default=None, max_length=255)


class CategoriaVeiculo(Log, table=True):
    __tablename__: str = "categorias_veiculo"  # type: ignore
    id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
    nome: str = Field(max_length=100, nullable=False)
    descricao: str | None = Field(default=None, max_length=255)
    icone: str | None = Field(default=None, max_length=255)


class VeiculoBase(Log, table=True):
    __tablename__: str = "veiculos_base"  # type: ignore
    id: int = Field(primary_key=True)

    # Categoria do veículo
    categoria: str | None = Field(default=None, max_length=50)  # Categoria conforme etiquetagem

    # Informações básicas do veículo
    marca: str = Field(max_length=100, nullable=False)
    modelo: str = Field(max_length=100, nullable=False)
    motor: str = Field(max_length=50, nullable=True)
    versao: str | None = Field(default=None, max_length=100)

    # Transmissão - conforme etiquetagem (M, A, DCT, MTA, CVT)
    transmissao_tipo: str | None = Field(default=None, max_length=10)  # M, A, DCT, MTA, CVT
    transmissao_velocidades: int | None = Field(default=None)  # Número de velocidades

    # Ar condicionado
    ar_condicionado: bool | None = Field(default=None)

    # Direção assistida - conforme etiquetagem (H, M, E, E-H)
    direcao_tipo: str | None = Field(default=None, max_length=10)  # H, M, E, E-H

    # Combustível - conforme etiquetagem (E, G, F)
    combustivel_tipo: str | None = Field(default=None, max_length=10)  # E, G, F

    # Emissões no escapamento - Poluentes
    emissoes_nmhc: float | None = Field(default=None)  # NMHC (g/km)
    emissoes_co: float | None = Field(default=None)  # CO (g/km)
    emissoes_nox: float | None = Field(default=None)  # NOx (g/km)
    reducao_relativa_limite: float | None = Field(default=None)  # Redução relativa ao limite

    # Emissões no escapamento - Gás Efeito Estufa
    co2_fossil_etanol: float | None = Field(default=None)  # CO2 fóssil etanol (g/km)
    co2_fossil_gasolina: float | None = Field(default=None)  # CO2 fóssil gasolina (g/km)

    # Quilometragem por litro - Etanol
    km_l_etanol_cidade: float | None = Field(default=None)  # Etanol cidade (km/l)
    km_l_etanol_estrada: float | None = Field(default=None)  # Etanol estrada (km/l)

    # Quilometragem por litro - Gasolina
    km_l_gasolina_cidade: float | None = Field(default=None)  # Gasolina cidade (km/l)
    km_l_gasolina_estrada: float | None = Field(default=None)  # Gasolina estrada (km/l)

    # Consumo energético
    consumo_energetico: float | None = Field(default=None)  # MJ/km

    # Classificação PBE
    classificacao_pbe_relativa: str | None = Field(default=None, max_length=20)  # Comparação relativa na categoria
    classificacao_pbe_absoluta: str | None = Field(default=None, max_length=20)  # Comparação absoluta geral

    # Selo CONPET de Eficiência Energética
    selo_conpet: bool | None = Field(default=None)

    # Campos legados (mantidos para compatibilidade)
    quantidade_portas: int = Field(default=4, nullable=True)
    # Categoria do veículo
    categoria_externa: str | None = Field(default=None, max_length=50)
    categoria_interna: str | None = Field(default=None, max_length=50)


class VeiculoMotorista(Log, table=True):
    __tablename__: str = "veiculos_motoristas"  # type: ignore
    id: int = Field(primary_key=True)
    placa: str = Field(index=True, max_length=20, unique=True)
    cor: str = Field(max_length=50)
    # motorista_id: int | None = Field(default=None, foreign_key="users.id")
