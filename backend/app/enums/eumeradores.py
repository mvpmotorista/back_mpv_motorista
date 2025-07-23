from enum import Enum


class TipoPerfilEnum(str, Enum):
    aluno = "aluno"
    professor = "professor"
    admin = "admin"
    coordenador = "coordenador"


class StatusEnum(str, Enum):
    ativo = "ativo"
    inativo = "inativo"


class FeriadoAbrangenciaEnum(str, Enum):
    Estadual = "estadual"
    Municipal = "municipal"
    Federal = "federal"
