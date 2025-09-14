@echo off
REM Script para subir o Docker Compose no WSL

REM Caminho do projeto no WSL
set PROJETO=/mnt/c/Projetos/Alef/MVP-CORRIDA/back_mpv_motorista/tileserver-gl

REM Comando que será executado no WSL
wsl -e sh -c "cd %PROJETO% && docker compose up --force-recreate"
pause
