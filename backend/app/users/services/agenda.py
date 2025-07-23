import calendar
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Tuple, List

from pydantic import BaseModel

from app.schemas.professor import CalendarioResponse
from app.datetime_utils import ensure_brt_timezone


class IntervaloAluno(BaseModel):
    data_ini: datetime
    data_fim: datetime


class IntervaloProfessor(BaseModel):
    data_ini: datetime
    data_fim: datetime
    id_professor: int


class Agenda:
    @classmethod
    def get_intervalos(cls, hora_ini: time, hora_fim: time, intervalo: timedelta) -> list:
        intervalos = []
        current = datetime.combine(datetime.today(), hora_ini)
        end = datetime.combine(datetime.today(), hora_fim)
        while current < end:
            intervalos.append((current.time(), (current + intervalo).time()))
            current += intervalo
        return intervalos

    @classmethod
    def get_periodo(cls, time_ini: time):
        # Manhã 1 - (08:00-10:30)
        # Manhã 2 - (10:45-13:15)
        # Tarde - (14:15-17:45)
        if time_ini > time(17, 45):
            return 'Noite'
        if time_ini > time(14, 14):
            return 'Tarde'
        if time_ini > time(10, 30):
            return 'Manhã 2'
        return 'Manhã 1'

    @classmethod
    def montar_calendario(cls, data_ini: date, date_fim: date, diponibilidade_atual) -> CalendarioResponse:
        weekday_abbr_pt = {
            calendar.MONDAY.value: 'seg',
            calendar.TUESDAY.value: 'ter',
            calendar.WEDNESDAY.value: 'qua',
            calendar.THURSDAY.value: 'qui',
            calendar.FRIDAY.value: 'sex',
            calendar.SATURDAY.value: 'sab',
            calendar.SUNDAY.value: 'dom',
        }
        intervalos = cls.get_intervalos(time(6, 0), time(22, 0), timedelta(minutes=15))
        calendario = []
        for i, f in intervalos:
            template = {"periodo": cls.get_periodo(i), "intervalo_ini": i, "intervalo_fim": f}
            next_data = data_ini
            while next_data < date_fim:
                is_disponivel = cls.verificar_disponibilidade(
                    data_fim=datetime.combine(next_data, f),
                    data_ini=datetime.combine(next_data, i),
                    diponibilidade_atual=diponibilidade_atual,
                )
                template[weekday_abbr_pt[next_data.weekday()]] = {'is_disponivel': is_disponivel}
                next_data = next_data + timedelta(days=1)
            calendario.append(template)
        disponibilidade = {
            'calendario': calendario,
            'dia_seg': data_ini,
            'dia_ter': data_ini + timedelta(days=1),
            'dia_qua': data_ini + timedelta(days=2),
            'dia_qui': data_ini + timedelta(days=3),
            'dia_sex': data_ini + timedelta(days=4),
            'dia_sab': data_ini + timedelta(days=5),
            'dia_dom': data_ini + timedelta(days=6),
            'dat_ini_prox_semana': data_ini + timedelta(days=7),
            'dat_fim_prox_semana': data_ini + timedelta(days=13),
            'dat_ini_semana_anterior': data_ini - timedelta(days=7),
            'dat_fim_semana_anterior': data_ini - timedelta(days=1),
        }
        return CalendarioResponse(**{'data': disponibilidade})

    @classmethod
    def verificar_disponibilidade(cls, data_ini, data_fim, diponibilidade_atual):
        for d in diponibilidade_atual:
            if d['dat_ini'] <= data_ini <= d['dat_fim'] and d['dat_ini'] <= data_fim <= d['dat_fim']:
                return True
        return False

    @classmethod
    def criar_agendamentos_futuro(
        cls, datas_aluno: list[IntervaloAluno], datas_professor: list[IntervaloProfessor]
    ) -> list[dict]:
        agendamentos = defaultdict(list)
        for data_aluno in datas_aluno:
            for data_professor in datas_professor:
                # Exemplo de lógica: verifica se o intervalo do aluno cabe no do professor
                if data_aluno.data_ini >= data_professor.data_ini and data_aluno.data_fim <= data_professor.data_fim:
                    agendamentos[data_aluno.data_ini, data_aluno.data_fim].append(data_professor.id_professor)

        return agendamentos
