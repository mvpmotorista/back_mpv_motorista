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

from app.api.events import add_event_listener
from app.api.main import api_router
from app.core.config import settings


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

# Rota para arquivos estáticos (fora do versionamento da API)
from app.api.routes.static import router as static_router

# Mount para arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

add_event_listener()
