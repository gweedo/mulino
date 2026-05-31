"""Auth router — login, logout, me."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from pizzeria.api.deps import CurrentOwner, cookie_secure, get_auth_use_case
from pizzeria.api.limiter import limiter
from pizzeria.api.schemas import LoginRequest, MeResponse
from pizzeria.application.use_cases.authenticate_owner import AuthenticateOwner

router = APIRouter()


@router.post("/login", status_code=200)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    auth: Annotated[AuthenticateOwner, Depends(get_auth_use_case)],
    secure: Annotated[bool, Depends(cookie_secure)],
) -> dict:
    token = await auth.execute(body.email, body.password)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=secure,
    )
    return {}


@router.post("/logout", status_code=204)
async def logout(
    _owner: CurrentOwner,
    response: Response,
    secure: Annotated[bool, Depends(cookie_secure)],
) -> None:
    response.delete_cookie(key="session", httponly=True, samesite="lax", secure=secure)


@router.get("/me", response_model=MeResponse)
async def me(owner: CurrentOwner) -> MeResponse:
    return MeResponse(id=owner.id, email=owner.email)
