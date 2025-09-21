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
# from app.core.models.driver import *  # noqa
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


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    print(configuration)
    current_tenant = 'public'
    with connectable.connect() as connection:
        if connection.dialect.name == "postgresql":
            print('set search_path to "%s"' % current_tenant)
            # set search path on the connection, which ensures that
            # PostgreSQL will emit all CREATE / ALTER / DROP statements
            # in terms of this schema by default

            connection.execute(text('set SESSION search_path to "%s"' % current_tenant))
            # in SQLAlchemy v2+ the search path change needs to be committed
            connection.commit()
        elif connection.dialect.name in ("mysql", "mariadb"):
            # set "USE" on the connection, which ensures that
            # MySQL/MariaDB will emit all CREATE / ALTER / DROP statements
            # in terms of this schema by default

            connection.execute(text('USE %s' % current_tenant))

        # make use of non-supported SQLAlchemy attribute to ensure
        # the dialect reflects tables in terms of the current tenant name
        connection.dialect.default_schema_name = current_tenant

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            version_table_schema=current_tenant,
            # include_object=validate_tenant(current_tenant),
        )

        with context.begin_transaction():
            context.run_migrations()


def validate_tenant(current_tenant):
    print('validar')

    def inner(object, name, type_, reflected, compare_to):
        result = object.schema == current_tenant
        return result

    return inner


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
