from sqlmodel import Field
from app.core.models.core import Log


# class Driver(Log, table=True):
#     __tablename__: str = "drivers"  # type: ignore
#     id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})

class Veichele(Log, table=True):
    __tablename__: str = "veicheles"  # type: ignore
    id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
    placa: str = Field(index=True, max_length=20, unique=True)
    model: str = Field(index=True, max_length=100)
    color: str = Field(index=True, max_length=50)
    year: int = Field(index=True)
    capacidade: int = Field(index=True)
    category: str = Field(index=True, max_length=50)
    is_avaliable: bool = Field(default=True)
    motorista_id: int | None = Field(default=None, foreign_key="drivers.id")

class ViecheleCategory(Log, table=True):
    __tablename__: str = "veichele_categories"  # type: ignore
    id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
    name: str = Field(index=True, max_length=50, unique=True)
    description: str = Field(index=True, max_length=255)


# class Ride(Log, table=True):
#     __tablename__: str = "rides"  # type: ignore
