# Seu código para CPFStr e CPFField (que está correto)
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_core import core_schema


class CPFStr(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, value: str) -> str:
        # ... (sua lógica de validação do CPF) ...
        cpf = ''.join(filter(str.isdigit, value))
        if len(cpf) != 11:
            raise ValueError("CPF deve conter 11 dígitos")

        if cpf == cpf[0] * 11:
            raise ValueError("CPF inválido: todos os dígitos iguais")

        def calc_digit(part: str) -> int:
            s = sum(int(d) * w for d, w in zip(part, range(len(part) + 1, 1, -1)))
            r = 11 - s % 11
            return r if r < 10 else 0

        d1 = calc_digit(cpf[:9])
        d2 = calc_digit(cpf[:9] + str(d1))

        if int(cpf[9]) != d1 or int(cpf[10]) != d2:
            raise ValueError("CPF inválido: dígito verificador não confere")

        return cpf


CPFField = Annotated[CPFStr, Field(description="CPF válido com 11 dígitos", example="123.456.789-09")]

# **Seu modelo PerfilAlunoCreate**
