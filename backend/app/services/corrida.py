from typing import Literal, List, Optional

# Regras de precificação por tipo de corrida
REGRAS_PRECO = {
    "UberX": {
        "tarifa_base": 4.0,
        "custo_por_km": 1.8,
        "custo_por_minuto": 0.4,
        "tarifa_minima": 8.0,
    },
    "Comfort": {
        "tarifa_base": 6.0,
        "custo_por_km": 2.2,
        "custo_por_minuto": 0.5,
        "tarifa_minima": 12.0,
    },
    "Black": {
        "tarifa_base": 10.0,
        "custo_por_km": 3.5,
        "custo_por_minuto": 0.8,
        "tarifa_minima": 20.0,
    },
    "Moto": {
        "tarifa_base": 2.5,
        "custo_por_km": 1.0,
        "custo_por_minuto": 0.25,
        "tarifa_minima": 5.0,
    },
}


def calcular_multiplicador(
    passageiros_ativos: int,
    motoristas_disponiveis: int,
    tempo_espera_min: float,
    recusas_motoristas: int,
) -> float:
    """Calcula o multiplicador dinâmico considerando demanda, espera e recusas."""
    if motoristas_disponiveis == 0:
        return 3.0  # máximo, sem motoristas

    razao = passageiros_ativos / motoristas_disponiveis

    # Baseado na razão de demanda
    if razao < 1:
        mult = 1.0
    elif razao < 1.5:
        mult = 1.2
    elif razao < 2:
        mult = 1.5
    elif razao < 3:
        mult = 2.0
    else:
        mult = 2.5

    # Ajuste pelo tempo médio de espera
    if tempo_espera_min > 10:
        mult += 0.2
    elif tempo_espera_min < 3:
        mult -= 0.1

    # Ajuste pelas recusas
    if recusas_motoristas > 5:  # muitos recusando → aumentar
        mult += 0.3
    elif recusas_motoristas > 2:
        mult += 0.1

    return max(1.0, min(mult, 3.0))  # entre 1.0 e 3.0


def calcular_preco(
    tipo_corrida: Literal["UberX", "Comfort", "Black", "Moto"],
    distancia_km: float,
    duracao_min: float,
    passageiros_ativos: int,
    motoristas_disponiveis: int,
    tempo_espera_min: float,
    recusas_motoristas: int = 0,
    taxa_combustivel_por_km: float = 0.0,
    taxa_plataforma: float = 2.0,
    pedagios: Optional[List[float]] = None,
    desconto: float = 0.0,
) -> float:
    """Calcula o preço da corrida no estilo Uber considerando todos os fatores."""
    regras = REGRAS_PRECO[tipo_corrida]

    # Multiplicador dinâmico
    multiplicador = calcular_multiplicador(
        passageiros_ativos, motoristas_disponiveis, tempo_espera_min, recusas_motoristas
    )

    # Preço base
    preco = (
        regras["tarifa_base"]
        + (distancia_km * (regras["custo_por_km"] + taxa_combustivel_por_km))
        + (duracao_min * regras["custo_por_minuto"])
    )

    # Aplica preço dinâmico
    preco *= multiplicador

    # Taxa da plataforma
    preco += taxa_plataforma

    # Pedágios
    if pedagios:
        preco += sum(pedagios)

    # Garante tarifa mínima
    preco = max(preco, regras["tarifa_minima"])

    # Aplica desconto
    preco -= desconto
    preco = max(preco, 0)

    return round(preco, 2)


# Exemplos de uso
print("UberX baixa demanda:", calcular_preco("UberX", 10, 15, 50, 100, 2, recusas_motoristas=0))
print("Comfort alta demanda:", calcular_preco("Comfort", 8, 20, 200, 100, 12, recusas_motoristas=6))
print("Black com pedágio:", calcular_preco("Black", 25, 40, 300, 100, 8, recusas_motoristas=3, pedagios=[5.0, 7.5]))
print("Moto com desconto:", calcular_preco("Moto", 5, 10, 120, 60, 5, recusas_motoristas=1, desconto=4.0))
