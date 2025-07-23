import re

from pydantic import BaseModel, Field, HttpUrl, computed_field
from pydantic_core import core_schema

from app.service.supabase import url_builder

last_dot = re.compile(r'\.(?=[^\.]*$)')


class UploadResponse(BaseModel):
    success: bool
    key: str
    url: HttpUrl
    path: str


class ColorHex(str):
    HEX_REGEX = re.compile(r'^#?[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$')

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError('Color must be a string')
        if not cls.HEX_REGEX.fullmatch(value):
            raise ValueError('Invalid hexadecimal color format. Expected format: #RRGGBB or RRGGBB')
        return value


class DocumentosOut(BaseModel):
    id: int
    nome: str
    descricao: str | None = None
    path: str = Field(..., exclude=True)  # usado internamente, mas omitido no dump
    versao: int

    @computed_field
    @property
    def url(self) -> str | None:
        if self.path:
            return url_builder(self.path)
        return None
