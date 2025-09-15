from typing import Any

from fastapi import APIRouter
from geoalchemy2 import Geography, Geometry
from pydantic import BaseModel
from sqlmodel import func, select, cast

from app.api.deps import AsyncSessionDep
from app.services.corrida import calcular_preco
from app.users.models.users import User

router = APIRouter(prefix="/corrida", tags=["corrida"])


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
            1000,  # 10 km em metros
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
    preco_confort = calcular_preco(
        "Comfort", distancia_km, duracao_min, passageiros_ativos, motoristas_disponiveis, tempo_espera_min
    )
    preco_economico = calcular_preco(
        "UberX", distancia_km, duracao_min, passageiros_ativos, motoristas_disponiveis, tempo_espera_min
    )
    preco_xl = calcular_preco(
        "Black", distancia_km, duracao_min, passageiros_ativos, motoristas_disponiveis, tempo_espera_min
    )

    retorno = [
        {
            'titulo': 'Corrida Confort',
            'tipo_veiculo': 'confort',
            'subtitulo': 'Veículo confortável para sua viagem',
            'valor': preco_confort,
            'motoristas_disponiveis': len([m for m in results if m.veiculo_id is not None]),
        },
        {
            'titulo': 'Corrida Econômico',
            'tipo_veiculo': 'economico',
            'subtitulo': 'Opção mais econômica',
            'valor': preco_economico,
            'motoristas_disponiveis': len([m for m in results if m.veiculo_id is not None]),
        },
        {
            'titulo': 'Corrida XL',
            'tipo_veiculo': 'xl',
            'subtitulo': 'Veículo maior para grupos',
            'valor': preco_xl,
            'motoristas_disponiveis': len([m for m in results if m.veiculo_id is not None]),
        },
    ]

    return {
        'opcoes_corrida': retorno,
        'total_motoristas_proximos': len(results),
        'coordenadas_busca': {'lat': localizacao.lat_ini, 'lon': localizacao.lon_ini},
    }
