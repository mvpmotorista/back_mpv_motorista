from enum import Enum
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session
from app.models.core import LogAtividade


class AcaoEnum(str, Enum):
    criar_contrato = "Criação de contrato"
    atualizar_contrato = "Atualização de contrato"
    deletar_contrato = "Exclusão de contrato"
    criar_aula = "Criação de aula"
    atualizar_aula = "Atualização de aula"
    deletar_aula = "Exclusão de aula"
    criar_aluno = "Criação de aluno"
    atualizar_aluno = "Atualização de aluno"
    deletar_aluno = "Exclusão de aluno"
    criar_professor = "Criação de professor"
    atualizar_professor = "Atualização de professor"
    deletar_professor = "Exclusão de professor"


async def execute_raw_query(q, params, session: AsyncSession):
    result = await session.execute(text(q), params=params)
    return result


async def get_detalhe(acao: AcaoEnum, tabela_id: str, session) -> str:
    match acao:
        case AcaoEnum.criar_contrato:
            return f"Contrato {tabela_id} criado."
        case AcaoEnum.atualizar_contrato:
            return f"Contrato {tabela_id} atualizado."
        case AcaoEnum.deletar_contrato:
            return f"Contrato {tabela_id} excluído."
        case AcaoEnum.criar_aula:
            return f"Aula {tabela_id} criada."
        case AcaoEnum.atualizar_aula:
            return f"Aula {tabela_id} atualizada."
        case AcaoEnum.deletar_aula:
            return f"Aula {tabela_id} excluída."
        case AcaoEnum.criar_aluno:
            return f"Aluno {tabela_id} criado."
        case AcaoEnum.atualizar_aluno:
            return f"Aluno {tabela_id} atualizado."
        case AcaoEnum.deletar_aluno:
            return f"Aluno {tabela_id} excluído."
        case AcaoEnum.criar_professor:
            return f"Professor {tabela_id} criado."
        case AcaoEnum.atualizar_professor:
            return f"Professor {tabela_id} atualizado."
        case AcaoEnum.deletar_professor:
            return f"Professor {tabela_id} excluído."
        case _:
            return "Ação desconhecida."


async def logar_atividade(perfil: int | None, acao: AcaoEnum, tabela_id: str):
    async with async_session() as session:
        try:
            await asyncio.sleep(4)  # Simulate a small delay for async operation
            detalhe = await get_detalhe(acao, tabela_id, session)
            l = LogAtividade(perfil_id=perfil, acao=acao, detalhe=detalhe)
            session.add(l)

            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f'Erro ao cadastrar aulas: {e}')
            raise e
        finally:
            await session.close()


async def logar_atividade2(obj):
    if not hasattr(obj, '_acao'):
        return
    async with async_session() as session:
        try:
            if hasattr(obj, '_acao'):
                detalhe = await get_detalhe(obj._acao, obj.id, session)
                l = LogAtividade(perfil_id=obj.updated_by, acao=obj._acao, detalhe=detalhe)
                session.add(l)
                await session.commit()
        except Exception as e:
            await session.rollback()
            print(f'Erro ao cadastrar aulas: {e}')
            raise e
        finally:
            await session.close()
