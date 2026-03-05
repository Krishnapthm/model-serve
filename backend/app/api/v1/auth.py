"""Auth router — signup, login, and current-user profile."""

from fastapi import APIRouter, Depends

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, UserRead
from app.services.auth import AuthService

router = APIRouter()


@router.post("/auth/signup", status_code=201)
async def signup(
    body: SignupRequest,
    auth_svc: AuthService = Depends(get_auth_service),
):
    """Create a user account and return a bearer auth session."""
    session = await auth_svc.signup(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
    )
    return {"data": session.model_dump(mode="json")}


@router.post("/auth/login")
async def login(
    body: LoginRequest,
    auth_svc: AuthService = Depends(get_auth_service),
):
    """Authenticate with email/password and return a bearer auth session."""
    session = await auth_svc.login(email=body.email, password=body.password)
    return {"data": session.model_dump(mode="json")}


@router.get("/auth/me")
async def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user profile."""
    return {"data": UserRead.model_validate(current_user).model_dump(mode="json")}
