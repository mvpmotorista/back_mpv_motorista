import asyncio
from datetime import datetime, date
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
import jwt
from pydantic import BaseModel, ConfigDict, Field, model_serializer
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    AsyncSessionDep,
    CurrentUser,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password

from app.users.models.perfis import Perfil
from app.users.models.users import (
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

# from app.schemas.perfis import PerfilMe
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(session: AsyncSessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count_result = await session.execute(count_statement)

    statement = select(User).offset(skip).limit(limit)
    users_result = await session.execute(statement)
    total_count = count_result.scalar_one()
    users_list = users_result.scalars().all()
    return UsersPublic(data=users_list, count=total_count)


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def create_user(*, session: AsyncSessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


class PatchUser(BaseModel):
    nome: str | None
    telefone: str | None = None
    data_nascimento: date | None = None
    genero: str | None = None

    @model_serializer
    def serialize(self):
        return {
            "full_name": self.nome,
            "telefone": self.telefone,
            "data_nascimento": self.data_nascimento,
            "genero": self.genero,
        }


class Localizacao(BaseModel):
    lat_ini: float
    lat_fim: float
    lon_ini: float
    lon_fim: float


@router.patch("/me")
async def update_user_me(*, session: AsyncSessionDep, user_in: PatchUser, current_user: CurrentUser) -> Any:
    """
    Update own user.
    """
    for key, value in user_in.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    await session.commit()
    return {}


@router.get("/me")
async def motoritas(*, session: AsyncSessionDep, localizacao: Localizacao, current_user: CurrentUser) -> Any:
    """
    Update own user.
    """
    retono = [
        {'tipo_veiculo': 1, 'qtd': 5, 'valor': 20.00},
        {'tipo_veiculo': 2, 'qtd': 3, 'valor': 30.00},
    ]
    return retono


@router.patch("/me/password", response_model=Message)
def update_password_me(*, session: AsyncSessionDep, body: UpdatePassword, current_user: CurrentUser) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the current one")
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


class UserMe(BaseModel):
    full_name: str | None = None
    telefone: str | None = None
    data_nascimento: date | None = None
    email: str | None = None
    genero: str | None = None

    @model_serializer
    def serialize(self):
        return {
            "nome": self.full_name,
            "telefone": self.telefone,
            "data_nascimento": self.data_nascimento,
            "genero": self.genero,
            "email": self.email,
        }


@router.get("/me", response_model=UserMe)
async def read_user_me(current_user: CurrentUser, session: AsyncSessionDep) -> Any:
    """
    Get current user.
    """
    user = current_user.model_dump()
    return UserMe(**user)


@router.delete("/me", response_model=Message)
def delete_user_me(session: AsyncSessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super users are not allowed to delete themselves")
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: AsyncSessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(user_id: uuid.UUID, session: AsyncSessionDep, current_user: CurrentUser) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: AsyncSessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="User with this email already exists")

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


class NewAcount(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    token: str


@router.post("/new_account", summary="Create a new account for passenger")
async def criar_conta(payload: NewAcount, session: AsyncSessionDep):
    decoded_payload = jwt.decode(payload.token, options={"verify_signature": False})
    u = User(
        id=decoded_payload['sub'],
        email=decoded_payload['email'],
        full_name=decoded_payload.get('full_name', ''),
        is_active=True,
        is_superuser=False,
        role='user',
        hashed_password='not_set',
    )
    session.add(u)
    try:
        await session.commit()
    except Exception as ex:
        return {"message": "Conta criada com sucesso!"}
        raise ex
        await session.rollback()
        raise HTTPException(status_code=400, detail="Erro ao salvar perfil")

    return {"message": "Conta criada com sucesso!"}
