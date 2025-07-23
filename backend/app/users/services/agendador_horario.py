from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import TypedDict

import polars as pl
from ortools.sat.python import cp_model
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session
from app.enums.eumeradores import FeriadoAbrangenciaEnum, StatusAulaEnum
from app.models.agenda import Disponibilidade
from app.models.aulas import Aula
from app.models.contrato import Contrato, ContratoProfessorLink
from app.models.core import Feriado, Municipio
from app.models.perfis import Perfil
from app.schemas.perfis import TipoAula


@dataclass
class FeriadoInfo:
    municipio_id: int
    abrangencia: str
    uf: str


class ProfessorMunicipioInfo(TypedDict):
    municipio_id: int
    uf: str


def slot2(h1: time, h2: time, dia=date(2025, 7, 10)):
    return (
        datetime.combine(dia, h1.replace(second=0, microsecond=0)),
        datetime.combine(dia, h2.replace(second=0, microsecond=0)),
    )


def minutos(d: datetime):
    return d.hour * 60 + d.minute


def intersecao(a_ini, a_fim, b_ini, b_fim):
    ini = max(a_ini, b_ini)
    fim = min(a_fim, b_fim)
    return (ini, fim) if ini + 1 < fim else None


def agendar_aulas_flexivel(janelas_alunos, janelas_professores, duracoes, aulas_fixas):
    model = cp_model.CpModel()
    aulas = {}
    intervalos_por_aluno = {}
    intervalos_por_prof = {}
    presence_por_prof = {}

    for aluno, prof, start_min, end_min, duracao in aulas_fixas:
        start = model.NewConstant(minutos(start_min))
        end = model.NewConstant(minutos(end_min))

        intervalo = model.NewIntervalVar(start, duracao, end, f'aula_fixa_{aluno}_{prof}_{start_min}')

        # Adicionar no conjunto de intervalos do professor para garantir que ele está ocupado
        intervalos_por_prof.setdefault(prof, []).append(intervalo)

        # (Opcional) se quiser garantir que o aluno também não tenha conflito
        intervalos_por_aluno.setdefault(aluno, []).append(intervalo)

    for (aluno, prof), duracao in duracoes.items():
        if aluno not in janelas_alunos or prof not in janelas_professores:
            continue

        for a_ini, a_fim in janelas_alunos[aluno]:
            for p_ini, p_fim, tipo, qtd_aula in janelas_professores[prof]:
                inter = intersecao(minutos(a_ini), minutos(a_fim), minutos(p_ini), minutos(p_fim))
                if inter:
                    start_min, end_max = inter
                    if end_max - start_min >= duracao:
                        latest_start = end_max - duracao

                        start = model.NewIntVar(start_min, latest_start, f'start_{aluno}_{prof}_{start_min}')
                        end = model.NewIntVar(start_min + duracao, end_max, f'end_{aluno}_{prof}_{start_min}')
                        presence = model.NewBoolVar(f'presenca_{aluno}_{prof}_{start_min}')

                        intervalo = model.NewOptionalIntervalVar(
                            start, duracao, end, presence, f'aula_{aluno}_{prof}_{start_min}'
                        )

                        key = (aluno, prof, tipo, start_min)
                        aulas[key] = (intervalo, presence, start, end)

                        intervalos_por_aluno.setdefault(aluno, []).append(intervalo)
                        intervalos_por_prof.setdefault(prof, []).append(intervalo)
                        presence_por_prof.setdefault((prof, qtd_aula), []).append(presence)

    # Restrições de numero maximo de aulas por professor
    for prof, qtd in presence_por_prof:
        model.Add(sum(presence_por_prof[(prof, qtd)]) < qtd + 1)
    # Restrições de conflito
    for lista in intervalos_por_aluno.values():
        model.AddNoOverlap(lista)
    for lista in intervalos_por_prof.values():
        model.AddNoOverlap(lista)

    # Objetivo: maximizar número de aulas
    presencas = [presence for (_, presence, _, _) in aulas.values()]
    model.Maximize(sum(presencas))

    # Resolver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print("Status:", solver.StatusName(status))
    print("Valor do objetivo:", solver.ObjectiveValue())
    print("Tempo de execução (s):", solver.WallTime())
    print("Número de conflitos:", solver.NumConflicts())
    print("Número de ramificações:", solver.NumBranches())
    print("Estatísticas detalhadas:\n", solver.ResponseStats())

    # Extrair resultados
    resultado = []
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        for (aluno, prof, tipo, _), (intervalo, presence, start, end) in aulas.items():
            if solver.Value(presence):
                ini = solver.Value(start)
                fim = solver.Value(end)
                resultado.append((aluno, prof, tipo, ini, fim))
    else:
        print("No solution found.")
    return resultado


if __name__ == '__main__':
    # Exemplo de uso

    # Função auxiliar para criar slots de aula
    def slot(h1, m1, h2, m2, dia=date(2025, 7, 10)):
        return (datetime.combine(dia, time(h1, m1)), datetime.combine(dia, time(h2, m2)))

    alunos = {
        'aluno1': [slot(8, 30, 10, 0), slot(19, 30, 20, 30)],
        'aluno2': [slot(10, 0, 11, 0)],
        'aluno3': [slot(9, 0, 10, 0)],
        'aluno4': [slot(9, 0, 10, 0)],
    }

    profs = {
        'prof1': [slot(8, 0, 12, 0), slot(18, 0, 23, 0)],
        'prof2': [slot(8, 0, 12, 0)],
    }
    duracoes = {}
    for aluno in alunos:
        for prof in profs:
            for a_ini, a_fim in alunos[aluno]:
                duracoes[(aluno, prof)] = int((a_fim - a_ini).total_seconds() // 60)

    aulas_fixas = []

    resultado = agendar_aulas_flexivel(alunos, profs, duracoes, aulas_fixas)

    for aluno, prof, ini, fim in resultado:
        h1, m1 = divmod(ini, 60)
        h2, m2 = divmod(fim, 60)
        print(f'{aluno} com {prof}: {h1:02d}:{m1:02d} até {h2:02d}:{m2:02d}')


def extrair_preferencias(contrato) -> list[tuple[int, date, time, time]]:
    preferencias = []
    if contrato.preferencia_semanal:
        data = contrato.data_inicio
        while data <= contrato.data_termino:
            for pref in contrato.preferencia_semanal:
                if data.weekday() == pref['dia_semana']:
                    preferencias.append(
                        (
                            contrato.aluno_id,
                            data,
                            time.fromisoformat(pref['hora_ini']),
                            time.fromisoformat(pref['hora_fim']),
                        )
                    )
            data += timedelta(days=1)
    elif contrato.data_especifica:
        for pref in contrato.data_especifica:
            dat_ini = datetime.fromisoformat(pref['dat_ini'])
            dat_fim = datetime.fromisoformat(pref['dat_fim'])
            preferencias.append(
                (
                    contrato.aluno_id,
                    dat_ini.date(),
                    dat_ini.time(),
                    dat_fim.time(),
                )
            )
    return preferencias


async def calcular_melhores_aulas(contrato_id: int, session: AsyncSession):
    contrato = await get_contrato(contrato_id, session)
    if not contrato:
        return
    preferencias = extrair_preferencias(contrato)
    if not preferencias:
        return
    result_professor_link, disponibilidades = await get_disponibilidades(contrato_id, session, contrato)
    if not disponibilidades:
        return
    map_feriados = await get_feriados(session, contrato)
    professor_municipio_map = await get_municipio_map(contrato_id, session)
    result_aulas = await get_aulas_realizadas(contrato_id, session)
    nova_disponibilidades = filtrar_disponibilidades(disponibilidades, map_feriados, professor_municipio_map)
    if not nova_disponibilidades:
        return
    map_aulas_dia = {}
    for x in result_aulas:
        map_aulas_dia.setdefault(x['data_ini'].date(), []).append(
            (x['data_ini'].time(), x['data_fim'].time(), x['professor_id'])
        )

    df_aluno = pl.DataFrame(preferencias, schema=['aluno_id', 'data', 'hora_ini', 'hora_fim'])

    df_professor = pl.DataFrame(
        [(d.perfil_id, d.dat_ini.date(), d.dat_ini.time(), d.dat_fim.time(), d.tipo) for d in nova_disponibilidades],
        schema=['professor_id', 'data', 'hora_ini', 'hora_fim', 'tipo'],
        orient="row",
    )
    records = [(pl.professor_id, pl.qtd_aula) for pl in result_professor_link.scalars().all()]
    df_professor_contrato = pl.DataFrame(records, schema=['professor_id', 'qtd_aula'], orient="row")

    df = (
        df_aluno.join(df_professor, on='data', how='inner')
        .join(df_professor_contrato, on='professor_id', how='inner')
        .rename(
            {
                'hora_ini': 'hora_ini_aluno',
                'hora_fim': 'hora_fim_aluno',
                'hora_ini_right': 'hora_ini',
                'hora_fim_right': 'hora_fim',
            }
        )
    )
    grouped = df.group_by('data', 'aluno_id', 'professor_id')
    aulas_alocadas = []
    for key, shape in grouped:
        professores = defaultdict(list)
        alunos = defaultdict(list)
        alunos_distinct = shape.select(['aluno_id', 'hora_ini_aluno', 'hora_fim_aluno', 'data']).unique()
        for row in alunos_distinct.iter_rows(named=True):
            alunos[row['aluno_id']].append(slot2(row['hora_ini_aluno'], row['hora_fim_aluno'], row['data']))

        professores_distinct = shape.select(
            ['professor_id', 'hora_ini', 'hora_fim', 'data', 'tipo', 'qtd_aula']
        ).unique()

        for row in professores_distinct.iter_rows(named=True):
            professores[row['professor_id']].append(
                (*slot2(row['hora_ini'], row['hora_fim'], row['data']), row['tipo'], row['qtd_aula'])
            )

        duracoes = {}
        for aluno in alunos:
            for prof in professores:
                for a_ini, a_fim in alunos[aluno]:
                    duracoes[(aluno, prof)] = int((a_fim - a_ini).total_seconds() // 60)

        aulas_fixas = []
        if key[0] in map_aulas_dia:
            for a_ini, a_fim, prof in map_aulas_dia[key[0]]:
                n_i, n_f = slot2(a_ini, a_fim, key[0])
                duracao = int((n_f - n_i).total_seconds() // 60)
                aulas_fixas.append((contrato.aluno_id, prof, n_i, n_f, duracao))

        aulas_possiveis = agendar_aulas_flexivel(alunos, professores, duracoes, aulas_fixas)

        for aula in aulas_possiveis:
            aluno, prof, tipo, ini, fim = aula
            dat_ini_aula = datetime.combine(key[0], time(0)) + timedelta(minutes=ini)
            dat_fim_aula = datetime.combine(key[0], time(0)) + timedelta(minutes=fim)
            print(dat_ini_aula, dat_fim_aula, aluno, prof)
            aulas_alocadas.append((dat_ini_aula, dat_fim_aula, aluno, prof, tipo))
    return aulas_alocadas


async def get_disponibilidades(contrato_id, session, contrato):
    stm_porfessor_link = select(ContratoProfessorLink).where(ContratoProfessorLink.contrato_id == contrato_id)
    result_professor_link = await session.execute(stm_porfessor_link)

    subquery = select(ContratoProfessorLink.professor_id).where(ContratoProfessorLink.contrato_id == contrato_id)
    stm_disponibilidade = select(Disponibilidade).where(
        Disponibilidade.perfil_id.in_(subquery), Disponibilidade.dat_ini >= contrato.data_inicio
    )
    result = await session.execute(stm_disponibilidade)
    disponibilidades = result.scalars().all()
    return result_professor_link, disponibilidades


async def get_aulas_realizadas(contrato_id, session):
    aulas_usadas = [StatusAulaEnum.agendada, StatusAulaEnum.reagendada, StatusAulaEnum.realizada]

    stm_aulas = select(Aula.data_ini, Aula.data_fim, Aula.professor_id).where(
        Aula.professor_id.in_(
            select(ContratoProfessorLink.professor_id).where(ContratoProfessorLink.contrato_id == contrato_id)
        ),
        Aula.status.in_(aulas_usadas),
        Aula.is_active.is_(True),
    )

    result_aulas = await session.execute(stm_aulas)
    result_aulas = result_aulas.mappings().all()
    return result_aulas


async def get_municipio_map(contrato_id, session) -> dict[int, ProfessorMunicipioInfo]:
    professores_municipio = await session.execute(
        select(Municipio.uf, Perfil.municipio_id, Perfil.id)
        .join(Municipio, Perfil.municipio_id == Municipio.id)
        .where(
            Perfil.id.in_(
                select(ContratoProfessorLink.professor_id).where(ContratoProfessorLink.contrato_id == contrato_id)
            )
        )
    )
    professor_municipio_map: dict[int, ProfessorMunicipioInfo] = {
        x.id: {"municipio_id": x.municipio_id, "uf": x.uf} for x in professores_municipio.all()
    }
    return professor_municipio_map


async def get_feriados(session, contrato) -> dict[date, list[FeriadoInfo]]:
    feriados = await session.execute(
        select(Feriado.municipio_id, Feriado.data, Feriado.abrangencia, Feriado.uf).where(
            Feriado.data.between(contrato.data_inicio, contrato.data_termino),
            Feriado.is_active.is_(True),
        )
    )
    feriados = feriados.all()
    map_feriados = {}
    for x in feriados:
        for x in feriados:
            feriado_info = FeriadoInfo(x.municipio_id, x.abrangencia, x.uf)
            map_feriados.setdefault(x.data, []).append(feriado_info)
    return map_feriados


def filtrar_disponibilidades(disponibilidades, map_feriados, professor_municipio_map):
    nova_disponibilidades = []
    for d in disponibilidades:
        if d.dat_ini.date() not in map_feriados:
            nova_disponibilidades.append(d)
        else:
            info = professor_municipio_map.get(d.perfil_id)
            if not info:
                nova_disponibilidades.append(d)
                continue

            municipio_id = info["municipio_id"]
            uf = info["uf"]
            for feriado in map_feriados[d.dat_ini.date()]:
                # feriado é um FeriadoInfo
                # Ignora disponibilidade se o feriado for federal, estadual (mesmo UF), ou municipal (mesmo município)
                if (
                    feriado.abrangencia == FeriadoAbrangenciaEnum.Federal.value
                    or (feriado.abrangencia == FeriadoAbrangenciaEnum.Estadual.value and feriado.uf == uf)
                    or (
                        feriado.abrangencia == FeriadoAbrangenciaEnum.Municipal.value
                        and feriado.municipio_id == municipio_id
                    )
                ):
                    break
            else:
                # Se não encontrou nenhum feriado que invalide a disponibilidade, adiciona
                nova_disponibilidades.append(d)
    return nova_disponibilidades


async def get_contrato(contrato_id, session) -> Contrato | None:
    result = await session.execute(select(Contrato).where(Contrato.id == contrato_id, Contrato.is_active == True))
    contrato = result.scalar_one_or_none()
    return contrato


async def cadastrar_aulas(contrato_id: int):
    async with async_session() as session:
        try:
            result = await calcular_melhores_aulas(contrato_id=contrato_id, session=session)
            if result is None:
                return
            for x in result:
                dat_ini, dat_fim, aluno, prof, tipo = x
                aula = Aula(
                    contrato_id=contrato_id,
                    professor_id=prof,
                    data_ini=dat_ini,
                    data_fim=dat_fim,
                    duracao_minutos=int((dat_fim - dat_ini).total_seconds() // 60),
                    duracao_minutos_real=0,
                    tipo=tipo,
                    status=StatusAulaEnum.agendada.value,
                )  # type: ignore
                session.add(aula)
                await session.commit()
        except Exception as e:
            await session.rollback()
            print(f'Erro ao cadastrar aulas: {e}')
            raise e
        finally:
            await session.close()
