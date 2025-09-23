import sys
import os

print(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
        )
    )
)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from logging.config import fileConfig

from sqlalchemy import engine_from_config, inspect, text
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
from app.database import Base

# from app.models. import User  # noqa
from app.core.config import settings  # noqa

# from app.core.models.core import *  # noqa
from app.users.models.users import *  # noqa
# from app.core.models.driver import *  # noqa

target_metadata = Base.metadata
# breakpoint()
print("target_metadata", target_metadata)
for table_name, table_obj in target_metadata.tables.items():
    print(f"Table: {table_name}, Schema: {table_obj.schema}")
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    return str(settings.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline() -> None:
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
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    def include_name(name, type_, parent_names):
        if type_ == "index":
            # this **will* include the default schema
            return True
        if type_ == "table":
            # this **will* include the default schema
            return name not in ["spatial_ref_sys", "alembic_version"]
        if type_ == "schema":
            # this **will* include the default schema
            return name in ["public", None]
        else:
            return True

    def include_object(object, name, type_, reflected, compare_to):
        if type_ == "index" and name == "idx_users_current_location":
            return False
        return True

    print(config.get_section(config.config_ini_section, {}))
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        connection.execute(text('set search_path to "public"'))
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # include_schemas=True,
            include_name=include_name,
            version_table_schema='public',
            include_object=include_object,
            # compare_type=True,
        )
        connection.dialect.default_schema_name = 'public'
        inspector = inspect(connectable)

        with context.begin_transaction():
            # breakpoint()
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
