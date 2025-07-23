import json

from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.users.models.users import User, UserCreate


def my_seralize(value):
    return json.dumps(value, default=str)


engine_async = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_size=5,
    max_overflow=1,
    json_serializer=my_seralize,
    connect_args={
        "connect_timeout": 10,
    },
    pool_timeout=20,
    pool_recycle=1800,
    pool_pre_ping=True,
    # echo=True,  # Set to False in production
    # echo_pool=True,  # Set to False in production
)


sync_maker = sessionmaker()

async_session = async_sessionmaker(engine_async, expire_on_commit=False, sync_session_class=sync_maker)


# def receive_after_insert(mapper, connection, target):
#     print("before commit")


# event.listen(sync_maker, "after_commit", receive_after_insert)
# # @event.listens_for(sync_maker, "after_insert")


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
