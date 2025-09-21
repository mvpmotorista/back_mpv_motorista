# run_autogenerate.py
from alembic.config import Config
from alembic import command
from pathlib import Path

# Caminho do seu projeto e do alembic.ini
BASE_DIR = Path(__file__).resolve().parent
ALEMBIC_INI = BASE_DIR / "alembic.ini"

# Configuração do Alembic
alembic_cfg = Config(str(ALEMBIC_INI))
alembic_cfg.set_main_option("script_location", "app/alembic")

# Mensagem da revisão
message = "check"

# Chama a revisão com autogenerate
command.upgrade(alembic_cfg, "head")

print("Revisão autogerada criada com sucesso!")
