@echo off
wsl -d Ubuntu --cd /mnt/c/Projetos/ALEF/MVP-CORRIDA/back_mpv_motorista/backend .venv/bin/python -m fastapi dev
pause
