import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path
from sqlalchemy import and_, case, distinct, func, or_, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import aliased

from app.api.deps import AsyncSessionDep, CurrentUser, ResourceAccess
from app.enums.eumeradores import StatusEnum, TipoPerfilEnum

# from app.models.core import Documentos
# from app.models.perfis import Perfil
from app.users.models.users import User
# from app.schemas.core import DocumentosOut
# from app.schemas.perfis import AlunoContratoOut, AlunoCreate, AlunoOut, AlunoPatch
# from app.service.aluno import email_cadastro_aluno
# from app.service.log_atividade import AcaoEnum

router = APIRouter(prefix="/alunos", tags=["alunos"])


# @router.post("", response_model=AlunoOut, status_code=201)
# async def criar_aluno(
#     session: AsyncSessionDep,
#     dados: AlunoCreate,
#     background_tasks: BackgroundTasks,
#     current_user: CurrentUser,
#     _=ResourceAccess('alunos'),
# ):
#     try:
#         user = User(
#             email=dados.email, hashed_password=str(uuid.uuid4()), is_active=True, is_superuser=True, role='aluno'
#         )
#         session.add(user)
#         await session.flush()
#         perfil = Perfil(
#             **dados.model_dump(),
#             user_id=user.id,
#             tipo=TipoPerfilEnum.aluno.value,
#             hash=uuid.uuid4(),
#             status_id=StatusEnum.ativo.value,
#         )
#         perfil.created_by = current_user.perfil_id
#         perfil.updated_by = current_user.perfil_id
#         perfil._acao = 'criar_aluno'
#         session.add(perfil)
#         await session.commit()
#         await session.refresh(perfil)
#         background_tasks.add_task(email_cadastro_aluno, aluno=dados)
#         return AlunoOut(**perfil.model_dump(by_alias=True, exclude={'user_id', 'id'}), status=perfil.status_id)

#     except IntegrityError as e:
#         await session.rollback()
#         if 'ix_user_email' in str(e.orig):
#             raise HTTPException(status_code=400, detail="Usuário com esse email já existe.")
#         raise e


# @router.patch("/{hash_aluno}", response_model=AlunoOut, status_code=200)
# async def patch_aluno(
#     session: AsyncSessionDep,
#     dados: AlunoPatch,
#     current_user: CurrentUser,
#     hash_aluno: uuid.UUID = Path(title="Hash do aluno"),
#     _=ResourceAccess('alunos'),
# ):
#     try:
#         perfil = await session.execute(select(Perfil).where(Perfil.hash == hash_aluno))
#         perfil = perfil.scalar_one_or_none()
#         if perfil is None:
#             raise HTTPException(status_code=404, detail="Anluo não encontrado.")
#         for key, value in dados.model_dump(exclude_unset=True).items():
#             if hasattr(perfil, key):
#                 setattr(perfil, key, value)
#         perfil.updated_by = current_user.perfil_id
#         perfil._acao = AcaoEnum.atualizar_aluno
#         await session.commit()
#         return AlunoOut(**perfil.model_dump(by_alias=True, exclude={'user_id'}))

#     except IntegrityError as e:
#         await session.rollback()
#         if 'ix_user_email' in str(e.orig):
#             raise HTTPException(status_code=400, detail="Usuário com esse email já existe.")
#         raise e


# @router.get("/{hash_aluno}", status_code=200, response_model=AlunoContratoOut)
# async def get_one_aluno(
#     session: AsyncSessionDep,
#     current_user: CurrentUser,
#     hash_aluno: uuid.UUID = Path(title="Hash do aluno"),
#     _=ResourceAccess('alunos'),
# ):
#     alunos = await session.execute(
#         select(
#             Perfil.id,
#             Perfil.nome,
#             Perfil.foto,
#             Perfil.hash,
#             Perfil.email,
#             Perfil.cor,
#             Perfil.telefone,
#             Perfil.email_secundario,
#             Perfil.telefone_secundario,
#             Perfil.arquivo,
#             Perfil.cidade,
#         ).where(Perfil.hash == hash_aluno, Perfil.tipo == TipoPerfilEnum.aluno, Perfil.is_active.is_(True))
#     )
#     aluno_data = alunos.mappings().first()
#     if aluno_data is None:
#         raise HTTPException(status_code=404, detail="Aluno não encontrado.")
#     documentos = await session.execute(
#         select(
#             Documentos.id,
#             Documentos.nome_final.label('nome'),
#             Documentos.path,
#             Documentos.descricao,
#             Documentos.versao,
#         ).where(Documentos.owner_id == aluno_data['id'], Documentos.is_active == True)
#     )
#     documentos_list = [DocumentosOut(**dict(doc)) for doc in documentos.mappings().all()]
#     status_case = case(
#         (Contrato.status == 'ativo', 0),
#         else_=1,
#     )
#     professores_ids_subq = (
#         select(ContratoProfessorLink.professor_id)
#         .where(ContratoProfessorLink.contrato_id == Contrato.id)
#         .correlate(Contrato)
#     )

#     # Subquery que agrega os nomes dos professores com base nos IDs
#     professores_subquery = (
#         select(func.array_agg(Perfil.nome)).where(Perfil.id.in_(professores_ids_subq)).scalar_subquery()
#     )
#     stm_contrato = (
#         select(
#             professores_subquery.label('professores'),
#             Contrato.data_inicio,
#             Contrato.data_termino,
#             Contrato.numero_aulas_semanais,
#             Contrato.status.label('status_contrato'),
#             Contrato.tipo_curso,
#         )
#         .where(Contrato.aluno_id == aluno_data['id'])
#         .order_by(status_case.asc(), Contrato.data_inicio.desc())
#         .limit(1)
#     )
#     contrato_result = await session.execute(stm_contrato)
#     cotrado_d = contrato_result.mappings().first() or {}
#     return AlunoContratoOut(**{**aluno_data, **cotrado_d}, documentos=documentos_list)


# @router.get("", response_model=list[AlunoContratoOut], status_code=200)
# async def alunos(
#     session: AsyncSessionDep,
#     current_user: CurrentUser,
#     background_tasks: BackgroundTasks,
#     _=ResourceAccess('alunos'),
# ):
#     status_case = case(
#         (Contrato.status == 'ativo', 0),
#         else_=1,
#     )
#     stm = (
#         select(
#             Perfil.nome,
#             Perfil.foto,
#             Perfil.hash,
#             # Perfil.status,
#             Perfil.email,
#             Perfil.cor,
#             Perfil.telefone,
#             Perfil.email_secundario,
#             Perfil.telefone_secundario,
#             Perfil.arquivo,
#             Perfil.cidade,
#             Contrato.data_inicio,
#             Contrato.data_termino,
#             Contrato.numero_aulas_semanais,
#             Contrato.status.label('status_contrato'),
#             Contrato.tipo_curso,
#         )
#         .distinct(Perfil.id)
#         .join(Contrato, Perfil.id == Contrato.aluno_id, isouter=True)
#         .where(Perfil.tipo == TipoPerfilEnum.aluno, Perfil.is_active.is_(True))
#     )
#     if current_user.role == 'aluno':
#         stm = stm.where(Perfil.id == current_user.perfil_id)

#     stm = stm.order_by(Perfil.id, status_case.asc(), Contrato.data_inicio.desc())
#     alunos = await session.execute(stm)

#     return [AlunoContratoOut(**a) for a in alunos.mappings().all()]


# @router.get("/{hash_aluno}/aulas")
# async def get_aulas(
#     session: AsyncSessionDep,
#     hash_aluno: uuid.UUID = Path(title="Hash do aluno"),
#     # data_ini: datetime = Query(None, description="Data inicial"),
#     # data_fim: datetime = Query(None, description="Data fim"),
# ):
#     Professor = aliased(Perfil)
#     Aluno = aliased(Perfil)
#     stmt = (
#         select(
#             Professor.nome.label("professor_nome"),
#             Aluno.nome.label("aluno_nome"),
#             Aula.id,
#             Aula.data_ini,
#             Aula.duracao_minutos,
#             Aula.duracao_minutos_real,
#             Aula.tipo,
#             Aula.status,
#         )
#         .join(Professor, Professor.id == Aula.professor_id)
#         .join(Contrato, Contrato.id == Aula.contrato_id)
#         .join(Aluno, Contrato.aluno_id == Aluno.id)
#         .where(
#             Aluno.hash == hash_aluno,
#             Aula.is_active == True,
#         )
#     )
#     result = await session.execute(stmt)
#     aulas = result.mappings().all()
#     return aulas
