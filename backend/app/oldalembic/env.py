import os
import sys

print(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
        )
    )
)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

from sqlmodel import SQLModel

# from app.models. import User  # noqa
from app.core.config import settings  # noqa
from app.core.models.core import *  # noqa
from app.users.models.users import *  # noqa
from app.core.models.driver import *  # noqa
# from app.core.models.corrida import *  # noqa
# from app.users.models.perfis import *  # noqa

target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    return str(settings.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # ...

    def include_name(name, type_, parent_names):
        """
        Função de callback que decide quais objetos incluir na migração.
        Ignora todos os schemas que não sejam 'public'.
        """
        if type_ == "schema":
            return name == "public" or name is None
        return True

    with connectable.connect() as connection:
        connection.execute(text('set SESSION search_path to "public"'  ))
            # in SQLAlchemy v2+ the search path change needs to be committed
        connection.commit()
        connection.dialect.default_schema_name = 'public'

        context.configure(
            connection=connection,
            # compare_type=True,
            target_metadata=target_metadata,
            version_table_schema='public',
            # Configurações para incluir schemas
            # include_schemas=True,
            # Usa a função de filtro para incluir apenas o schema 'public'
            include_name=include_name,
            include_object=validate_tenant('public'),
        )
        # with connectable.connect() as connection:
        #     context.configure(
        #         connection=connection, target_metadata=target_metadata, compare_type=True
        #     )


        with context.begin_transaction():
            context.run_migrations()


def validate_tenant(current_tenant):
    print('validar')

    def inner(object, name, type_, reflected, compare_to):
        # breakpoint()
        if type_ != 'table':
            return True
        print(1,object.schema, current_tenant)
        result = object.schema == current_tenant
        return result

    return inner


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
