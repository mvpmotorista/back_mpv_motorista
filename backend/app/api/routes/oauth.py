from datetime import timedelta
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

from app.api.deps import AsyncSessionDep
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.users.models.users import Token, User
from app import crud


router = APIRouter(prefix="/auth", tags=["auth"]) 


oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", response_model=Token)
async def google_callback(request: Request, session: AsyncSessionDep):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo")
        if not userinfo:
            # Fallback: fetch userinfo endpoint
            resp = await oauth.google.get("userinfo", token=token)
            userinfo = resp.json() if resp else None
    except Exception:
        raise HTTPException(status_code=400, detail="Google OAuth2 authentication failed")

    if not userinfo or not userinfo.get("email"):
        raise HTTPException(status_code=400, detail="Google account has no email available")

    email = userinfo["email"].lower()
    full_name = userinfo.get("name")

    user = await crud.get_user_by_email(session=session, email=email)
    if not user:
        # Create a local user with a random password
        random_password = secrets.token_urlsafe(16)
        hashed_password = get_password_hash(random_password)
        user = User(email=email, full_name=full_name, hashed_password=hashed_password, is_active=True)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = security.create_access_token(user.id, expires_delta=access_token_expires)

    # Mobile/web: if FRONTEND_OAUTH_REDIRECT_URL is defined, redirect with token
    if settings.FRONTEND_OAUTH_REDIRECT_URL:
        url = settings.FRONTEND_OAUTH_REDIRECT_URL.rstrip('/')
        return RedirectResponse(url=f"{url}?provider=google&token={jwt_token}")

    # Default: API returns JSON token
    return Token(access_token=jwt_token)


