from supabase import create_client, Client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def on_update(payload):
    print("🚦 Atualização detectada:", payload)
    nova_linha = payload["new"]
    if nova_linha["status"] == "iniciado":
        print("➡️ Corrida iniciada, chamando motoristas...")

# Inscrever no Realtime
supabase \
    .table("corridas") \
    .on("UPDATE", on_update) \
    .subscribe()

# Mantém o worker rodando
import time
while True:
    time.sleep(1)
