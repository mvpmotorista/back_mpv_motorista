from pathlib import Path

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.api.events import add_event_listener


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    else:
        return f"{route.name}"


print(settings.SQLALCHEMY_DATABASE_URI)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
add_event_listener()

# build_path = Path('app') / 'build' / 'web'


# @app.get("/{full_path:path}")
# async def spa_handler(full_path: str):
#     file_path = build_path / full_path

#     # Se o arquivo existe, serve diretamente (JS, WASM, assets, etc.)
#     if file_path.is_file():
#         return FileResponse(file_path)

#     # Se for uma rota "virtual" (SPA), retorna o index.html
#     index_path = build_path / "index.html"
#     return FileResponse(index_path, headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
