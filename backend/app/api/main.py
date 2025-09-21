from fastapi import APIRouter

from app.api.routes import login, private, roteamento, users, utils, core, oauth,driver
from app.core.config import settings
from app.api.routes import perfil

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(oauth.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(perfil.router)
api_router.include_router(core.router)
api_router.include_router(roteamento.router)
api_router.include_router(driver.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
