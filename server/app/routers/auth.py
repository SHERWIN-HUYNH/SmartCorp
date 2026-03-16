from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.schemas import AuthResponse, LoginRequest, MessageResponse, SignupRequest, TokenResponse, UserResponse
from app.services.auth_service import (
    authenticate_user,
    clear_refresh_token,
    create_user,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    get_user_by_email,
    get_user_by_id,
    store_refresh_token,
    validate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/", domain=settings.COOKIE_DOMAIN)
    response.delete_cookie("refresh_token", path="/", domain=settings.COOKIE_DOMAIN)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: SignupRequest, response: Response, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(user_data.email, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = create_user(user_data, db)
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    store_refresh_token(user, refresh_token, db)

    _set_auth_cookies(response, access_token, refresh_token)
    return AuthResponse(user=UserResponse.model_validate(user), token_type="bearer")


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(payload.email, payload.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    store_refresh_token(user, refresh_token, db)

    _set_auth_cookies(response, access_token, refresh_token)
    return AuthResponse(user=UserResponse.model_validate(user), token_type="bearer")


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    payload = decode_refresh_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = get_user_by_id(user_id, db)
    if not user or not validate_refresh_token(user, refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access = create_access_token(str(user.id))
    new_refresh = create_refresh_token(str(user.id))
    store_refresh_token(user, new_refresh, db)

    _set_auth_cookies(response, new_access, new_refresh)
    return TokenResponse(access_token=new_access, refresh_token=new_refresh, token_type="bearer")


@router.post("/logout", response_model=MessageResponse)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if refresh_token:
        payload = decode_refresh_token(refresh_token)
        if payload and payload.get("sub"):
            user = get_user_by_id(payload["sub"], db)
            if user:
                clear_refresh_token(user, db)

    _clear_auth_cookies(response)
    return MessageResponse(detail="Logged out")


# 
@router.get("/me", response_model=UserResponse)
def me(access_token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    payload = decode_access_token(access_token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user = get_user_by_id(payload.get("sub"), db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return UserResponse.model_validate(user)