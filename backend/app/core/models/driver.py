from sqlmodel import Field, Relationship
from app.core.models.core import Log


class CategoriaCorrida(Log, table=True):
    __tablename__: str = "categorias_corridas"  # type: ignore
    id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
    nome: str = Field(max_length=100, nullable=False)
    descricao: str | None = Field(default=None, max_length=255)
    icone: str | None = Field(default=None, max_length=255)


class CategoriaVeiculo(Log, table=True):
    __tablename__: str = "categorias_veiculo"  # type: ignore
    id: int = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
    nome: str = Field(max_length=100, nullable=False)
    descricao: str | None = Field(default=None, max_length=255)
    icone: str | None = Field(default=None, max_length=255)


