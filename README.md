# FastAPI Project Template

Um template moderno e robusto para projetos FastAPI seguindo as melhores práticas de desenvolvimento, incluindo Clean Architecture, Repository Pattern e estrutura escalável.

## 🚀 Características Atuais

- ✅ **FastAPI** - Framework web moderno e de alta performance
- ✅ **PostgreSQL** - Banco de dados relacional
- ✅ **JWT Authentication** - Sistema de login/autenticação
- ✅ **Repository Pattern** - Abstração da camada de dados
- ✅ **SQLAlchemy** - ORM para interação com banco de dados
- ✅ **Alembic** - Migrations de banco de dados
- ✅ **Pydantic** - Validação de dados e serialização

## 🔮 Roadmap - Próximas Implementações

- ☐ **Multi-tenant Architecture** - Suporte para múltiplos inquilinos/organizações
- ☐ **UV Package Manager** - Migração do Poetry para UV (gerenciador mais rápido)
- ☐ **Pytest** - Framework de testes completo
- ☐ **Docker** - Containerização
- ☐ **Logging** - Sistema de logs estruturado



## 🛠️ Configuração do Ambiente

### Pré-requisitos

- Python 3.11+
- Poetry (futuramente será migrado para UV)
- PostgreSQL
- Docker (opcional - será implementado)

### Instalação

1. **Clone o template:**
```bash
git clone <seu-repositorio>
cd seu-projeto-fastapi
```

2. **Instale as dependências:**
```bash
poetry install
```

3. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. **Configure o banco de dados:**
```bash
# Execute as migrações
poetry run alembic upgrade head
```

5. **Instale os hooks do pre-commit:**
```bash
# Será implementado nas próximas versões
# poetry run pre-commit install
```

## 🚀 Estado Atual do Template

**Versão:** 0.1.0 (MVP)

### ✅ Implementado
- Sistema de autenticação com JWT
- Integração com PostgreSQL
- Repository Pattern básico
- Estrutura base do projeto
- Modelos de usuário e autenticação

### 🔄 Em Desenvolvimento
Este template está em desenvolvimento ativo. As próximas versões incluirão as funcionalidades listadas no roadmap acima.

## 🚀 Executando a Aplicação

### Modo Desenvolvimento

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Com Docker

```bash
# Docker será implementado nas próximas versões
# docker-compose up --build
```

A aplicação estará disponível em `http://localhost:8000`

- **Documentação da API:** `http://localhost:8000/docs`
- **Documentação alternativa:** `http://localhost:8000/redoc`

## 🧪 Testes

```bash
# Testes serão implementados nas próximas versões
# poetry run pytest
```

Para cobertura de código:

```bash
# poetry run pytest --cov=app --cov-report=html
```

## 📊 Migrações de Banco de Dados

### Criar uma nova migração:
```bash
poetry run alembic revision --autogenerate -m "Descrição da migração"
```

### Aplicar migrações:
```bash
poetry run alembic upgrade head
```

### Reverter migração:
```bash
poetry run alembic downgrade -1
```

## 🔧 Configurações

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security  
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
PROJECT_NAME="FastAPI Template"
VERSION=0.1.0
DEBUG=True

# Multi-tenant (será implementado)
# TENANT_STRATEGY=subdomain  
# DEFAULT_TENANT=main
```

## 🏗️ Arquitetura

### Repository Pattern

O template implementa o Repository Pattern para abstrair o acesso a dados:

```python
# repositories/base.py
class BaseRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, id: int):
        # Implementação base
        pass

# repositories/user.py  
class UserRepository(BaseRepository):
    def get_by_email(self, email: str):
        # Implementação específica
        pass
```

### Services Layer

A camada de serviços contém a lógica de negócio:

```python
# services/user.py
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user_data: UserCreate):
        # Lógica de negócio
        pass
```

### Dependency Injection

Utilizamos o sistema de dependências do FastAPI:

```python
# api/deps.py
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

# endpoints/users.py
@router.post("/users/")
def create_user(
    user_service: UserService = Depends(get_user_service)
):
    # Usar o serviço
    pass
```

## 📝 Como Usar Este Template

1. **Personalize o projeto:**
   - Altere o nome do projeto em `pyproject.toml`
   - Atualize as configurações em `app/config/settings.py`
   - Modifique as variáveis de ambiente conforme necessário

2. **Adicione seus modelos:**
   - Crie novos modelos em `app/models/`
   - Defina os schemas em `app/schemas/`
   - Implemente repositories em `app/repositories/`
   - Adicione serviços em `app/services/`
   - Crie as rotas em `app/api/v1/endpoints/`

3. **Configure o banco de dados:**
   - Ajuste a configuração em `app/config/database.py`
   - Execute as migrações necessárias

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas, por favor:

1. Verifique a documentação
2. Procure em issues existentes
3. Crie uma nova issue com detalhes do problema

## 📚 Recursos Adicionais

- [Documentação do FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Poetry](https://python-poetry.org/)

---

**Desenvolvido com ❤️ usando FastAPI**