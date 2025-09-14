@echo off
REM Ajuste a porta se necessário
set PORT=8000

REM Abre o quick tunnel (gera subdomínio trycloudflare aleatório)
cloudflared tunnel --url http://localhost:%PORT%
pause