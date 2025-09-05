from fastapi import APIRouter, HTTPException, status, Path
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from typing import List
from uuid import uuid4
from fastapi import Body

# /home/hian/back_mpv_motorista/backend/app/api/routes/roteamento.py

router = APIRouter(prefix="/motoristas", tags=["roteamento"])


class Geolocalizacao(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude em graus")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude em graus")
    timestamp: Optional[datetime] = Field(None, description="Timestamp ISO8601")
    velocidade: Optional[float] = Field(None, ge=0, description="Velocidade em m/s")
    heading: Optional[float] = Field(None, ge=0, le=360, description="Direção em graus")


@router.post(
    "/{motorista_id}/localizacao",
    status_code=status.HTTP_201_CREATED,
    summary="Recebe a geolocalização de um motorista",
)
async def receber_localizacao(
    motorista_id: int = Path(..., description="ID do motorista"),
    geo: Geolocalizacao = ...,
):
    """
    Endpoint que recebe a posição do motorista.
    Integre aqui com sua camada de persistência ou serviço de roteamento.
    """
    try:
        registro = {
            "motorista_id": motorista_id,
            "latitude": geo.latitude,
            "longitude": geo.longitude,
            "timestamp": geo.timestamp or datetime.utcnow(),
            "velocidade": geo.velocidade,
            "heading": geo.heading,
        }

        # TODO: salvar registro no banco ou enviar para serviço de telemetria
        # await salvar_localizacao_no_db(registro)

        return {"status": "ok", "data": registro}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao processar localização")


class SolicitacaoCorrida(BaseModel):
    pontos: List[Geolocalizacao] = Field(..., min_items=2, description="Lista de pontos de parada (mínimo 2)")


@router.post(
    "/{passageiro_id}/corrida",
    status_code=status.HTTP_201_CREATED,
    summary="Solicita uma corrida para um passageiro com 2 ou mais pontos de parada",
)
async def solicitar_corrida(
    passageiro_id: int = Path(..., description="ID do passageiro"),
    solicitacao: SolicitacaoCorrida = Body(...),
):
    try:
        if len(solicitacao.pontos) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Deve fornecer pelo menos 2 pontos de parada",
            )

        corrida_id = str(uuid4())
        corrida = {
            "id": corrida_id,
            "passageiro_id": passageiro_id,
            "pontos": [p.dict() for p in solicitacao.pontos],
            "requested_at": datetime.utcnow(),
            "status": "pendente",
        }

        # TODO: persistir corrida no banco ou enviar para serviço de despacho
        # await criar_corrida_no_sistema(corrida)

        return {"status": "ok", "data": corrida}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao processar solicitação de corrida")
