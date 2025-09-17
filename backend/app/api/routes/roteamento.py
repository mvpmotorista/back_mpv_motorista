from typing import Any
import uuid

from fastapi import APIRouter
from geoalchemy2 import Geography, Geometry
from pydantic import BaseModel
from sqlmodel import func, select, cast

from app.api.deps import AsyncSessionDep, CurrentUser
from app.services.corrida import calcular_preco
from app.users.models.users import User

router = APIRouter(prefix="/corrida", tags=["corrida"])


fake_categorias = [
    {
        'id': uuid.UUID('22f5cb69-d97b-4753-a148-398a387b3ceb'),
        "tarifa_base": 4.0,
        "custo_por_km": 1.8,
        "custo_por_minuto": 0.4,
        "tarifa_minima": 8.0,
        'titulo': 'Confort',
        'subtitulo': '...',
        'icone': 'confort.json',
    },
    {
        'id': uuid.UUID('716f1605-2be5-47f3-8e1f-6c7bc76736f2'),
        "tarifa_base": 4.0,
        "custo_por_km": 1.8,
        "custo_por_minuto": 0.4,
        "tarifa_minima": 8.0,
        'titulo': 'Confort M',
        'subtitulo': '...',
        'icone': 'woman.json',
    },
    {
        'id': uuid.UUID('a59af7b3-2895-46e1-bf44-86b8d171613b'),
        "tarifa_base": 6.0,
        "custo_por_km": 2.2,
        "custo_por_minuto": 0.5,
        "tarifa_minima": 12.0,
        'titulo': 'XL',
        'subtitulo': '...',
        'icone': 'xl.json',
    },
    {
        'id': uuid.UUID('2b05c586-203e-45cd-8cf0-ce9cecd153e5'),
        "tarifa_base": 10.0,
        "custo_por_km": 3.5,
        "custo_por_minuto": 0.8,
        "tarifa_minima": 20.0,
        'titulo': 'Economico',
        'subtitulo': '...',
        'icone': 'economico.json',
    },
    {
        'subtitulo': '...',
        'id': uuid.UUID('2b05c586-203e-45cd-8cf0-ce9cecd153e5'),
        "tarifa_base": 2.5,
        "custo_por_km": 1.0,
        "custo_por_minuto": 0.25,
        "tarifa_minima": 5.0,
        'titulo': 'MOTO',
        'icone': 'moto.json',
    },
]


class Localizacao(BaseModel):
    lat_ini: float
    lat_fim: float
    lon_ini: float
    lon_fim: float
    endereco_inicio: str | None = None
    endereco_fim: str | None = None
    distancia: float | None = None
    duracao: float | None = None


@router.post("/cotar")
async def cotar_corrida(
    *,
    session: AsyncSessionDep,
    localizacao: Localizacao,
) -> Any:
    """
    Busca motoristas próximos usando coordenadas geográficas.
    """
    # Criar ponto de referência a partir das coordenadas de início
    ref_point = func.ST_SetSRID(func.ST_MakePoint(localizacao.lat_ini, localizacao.lon_ini), 4326)

    # Query para buscar motoristas próximos (dentro de 10km)
    statement = select(User.id).where(
        User.is_active,  # Apenas usuários ativos
        func.ST_DWithin(
            cast(User.current_location, Geography(geometry_type="POINT", srid=4326)),
            cast(ref_point, Geography(geometry_type="POINT", srid=4326)),
            10000,  # 10 km em metros
        ),
    )

    results = (await session.execute(statement)).all()

    # Parâmetros para cálculo de preço
    distancia_km = localizacao.distancia or 0
    duracao_min = localizacao.duracao or 0
    passageiros_ativos = 50  # Valor padrão
    motoristas_disponiveis = len(results)
    tempo_espera_min = 5.0  # Valor padrão

    # Calcular preços para diferentes tipos de veículo
    for x in fake_categorias:
        # x['icone'] = /x['icone']
        x['preco'] = calcular_preco(
            x,
            distancia_km,
            duracao_min,
            passageiros_ativos,
            motoristas_disponiveis,
            tempo_espera_min,
            taxa_combustivel_por_km=6.19,
        )

    return fake_categorias


class ConfirmarCorrida(BaseModel):
    lat_ini: float
    lat_fim: float
    lon_ini: float
    lon_fim: float
    endereco_inicio: str | None = None
    endereco_fim: str | None = None
    distancia: float | None = None
    duracao: float | None = None
    veiculo_id: uuid.UUID


# @router.post("/reservar-corrida")
# async def reservar_corrida(
#     *,
#     session: AsyncSessionDep,
#     localizacao: Localizacao,
# ) -> Any:

#     ref_point = func.ST_SetSRID(func.ST_MakePoint(localizacao.lat_ini, localizacao.lon_ini), 4326)
#     # Query para buscar motoristas próximos (dentro de 10km)
#     statement = select(User.id).where(
#         User.is_active,  # Apenas usuários ativos
#         func.ST_DWithin(
#             cast(User.current_location, Geography(geometry_type="POINT", srid=4326)),
#             cast(ref_point, Geography(geometry_type="POINT", srid=4326)),
#             10000,  # 10 km em metros
#         ),
#     )
#     return {}


class Reserva(BaseModel):
    id: uuid.UUID


@router.post("/reservar")
async def reservar_corrida(*, session: AsyncSessionDep, current_user: CurrentUser, dados: Reserva) -> Any:
    current_user.status_corrida = 'aguardando'
    await session.commit()
    return {}


@router.post("/cancelar")
async def cancelar_corrida(*, session: AsyncSessionDep, current_user: CurrentUser) -> Any:
    current_user.status_corrida = 'cancelar'
    await session.commit()
    return {}


@router.get("/consultar")
async def consultar_corrida(*, session: AsyncSessionDep, current_user: CurrentUser) -> Any:
    # current_user.status_corrida = 'aguardando'
    retorno_exemplo = {
        'foto_motorista': 'url',
        'nome_motorista': 'Fulano de Tal',
        'placa_veiculo': 'ABC-1234',
        'modelo_veiculo': 'Toyota Corolla',
        'tempo_chegada_min': 5,
        'cor_veiculo': 'Prata',
    }
    return retorno_exemplo

@router.post("/finalizar")
async def finalizar_corrida(*, session: AsyncSessionDep, current_user: CurrentUser) -> Any:
    # current_user.status_corrida = 'aguardando'
    retorno_exemplo = {
        'foto_motorista': 'url',
        'nome_motorista': 'Fulano de Tal',
        'placa_veiculo': 'ABC-1234',
        'modelo_veiculo': 'Toyota Corolla',
        'tempo_chegada_min': 5,
        'cor_veiculo': 'Prata',
    }
    return retorno_exemplo
