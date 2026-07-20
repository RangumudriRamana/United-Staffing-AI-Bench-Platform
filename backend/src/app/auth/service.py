from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories import UserRepository
from app.auth.schemas import LoginRequest, RegisterRequest
from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import AppException
from app.models.user import User
from app.shared.unit_of_work import UnitOfWork


class AuthenticationService:
    """
    Handles authentication business workflows.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.uow = UnitOfWork(db)
        self.users = UserRepository(db)

    async def register(
        self,
        request: RegisterRequest,
    ) -> User:
        existing = await self.users.get_by_email(request.email)

        if existing:
            raise AppException(
                message="Email is already registered.",
                error_code="EMAIL_ALREADY_EXISTS",
                status_code=409,
            )

        user = User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            hashed_password=hash_password(request.password),
        )

        await self.users.add(user)

        await self.uow.commit()
        await self.uow.refresh(user)

        return user

    async def login(
        self,
        request: LoginRequest,
    ) -> tuple[str, User]:  # 1. Update return type hint
        user = await self.users.get_by_email(request.email)

        if user is None:
            raise AppException(
                message="Invalid email or password.",
                error_code="INVALID_CREDENTIALS",
                status_code=401,
            )

        if not verify_password(
            request.password,
            user.hashed_password,
        ):
            raise AppException(
                message="Invalid email or password.",
                error_code="INVALID_CREDENTIALS",
                status_code=401,
            )

        if not user.is_active:
            raise AppException(
                message="User account is inactive.",
                error_code="ACCOUNT_DISABLED",
                status_code=403,
            )

        token = create_access_token(user.public_id)
        return token, user

    async def get_current_user(
        self,
        public_id,
    ) -> User:
        user = await self.users.get_by_public_id(public_id)

        if user is None:
            raise AppException(
                message="User not found.",
                error_code="USER_NOT_FOUND",
                status_code=404,
            )

        return user