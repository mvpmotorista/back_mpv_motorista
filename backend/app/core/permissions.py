from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"


class Action(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


Permission = tuple[Role, str, Action]


# Definição das permissões
permissoes_rbac: set[Permission] = set()
