"""User authentication service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import AuthSession, UserRead
from app.utils.exceptions import InvalidCredentialsError, UserAlreadyExistsError


class AuthService:
    """Handles user signup, login, and auth token creation."""

    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    @staticmethod
    def _normalize_email(email: str) -> str:
        """Normalize user email for consistent lookups."""
        return email.strip().lower()

    def _build_session(self, user: User) -> AuthSession:
        """Create an auth session payload for an authenticated user."""
        token = create_access_token(
            subject=str(user.id),
            secret_key=self.settings.secret_key,
            expires_minutes=self.settings.access_token_expire_minutes,
        )
        return AuthSession(
            access_token=token,
            token_type="bearer",
            user=UserRead.model_validate(user),
        )

    async def signup(
        self, email: str, password: str, full_name: str | None = None
    ) -> AuthSession:
        """Create a new user account and return a login session.

        Args:
            email: User email.
            password: Plaintext password.
            full_name: Optional display name.

        Returns:
            Auth session payload with bearer token and user details.

        Raises:
            UserAlreadyExistsError: If the email already exists.
        """
        normalized_email = self._normalize_email(email)
        result = await self.db.execute(
            select(User).where(User.email == normalized_email)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            raise UserAlreadyExistsError("An account with this email already exists")

        user = User(
            email=normalized_email,
            full_name=full_name.strip() if full_name else None,
            password_hash=hash_password(password),
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return self._build_session(user)

    async def login(self, email: str, password: str) -> AuthSession:
        """Authenticate credentials and return a login session.

        Args:
            email: User email.
            password: Plaintext password.

        Returns:
            Auth session payload with bearer token and user details.

        Raises:
            InvalidCredentialsError: If credentials are invalid.
        """
        normalized_email = self._normalize_email(email)
        result = await self.db.execute(
            select(User).where(User.email == normalized_email, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        return self._build_session(user)
