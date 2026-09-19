from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import AuthSession
from app.auth.repositories import UserRepository
from app.auth.schemas import LoginRequest, RegisterRequest
from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.audit.enums import AuditActionType
from app.audit.schemas import AuditRecordCreatePayload
from app.audit.service import AuditService


from app.core.exceptions import AppException
from app.models.user import User
from app.shared.unit_of_work import UnitOfWork

from datetime import UTC, datetime, timedelta
from app.core.config import get_settings

settings = get_settings()

class AuthenticationService:
    """
    Handles authentication business workflows.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.uow = UnitOfWork(db)
        self.users = UserRepository(db)
        self.audit_service = AuditService(db)

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

        token, jti = create_access_token(user.public_id)

        session = AuthSession(
            user_id=user.id,
            jti=jti,
            expires_at=datetime.now(UTC)
            + timedelta(minutes=settings.access_token_expire_minutes),
        )

        self.uow.db.add(session)

        await self.audit_service.write_audit_entry(
            AuditRecordCreatePayload(
                actor_user_id=user.id,
                action_type=AuditActionType.LOGIN,
                source_context="AUTH_SERVICE",
                entity_type="USER",
                entity_public_id=str(user.public_id),
                entity_version=await self.audit_service.get_next_entity_version(
                    entity_type="USER",
                    entity_public_id=str(user.public_id),
                ),
                before_snapshot_json=None,
                after_snapshot_json={
                    "public_id": str(user.public_id),
                    "email": user.email,
                    "is_active": user.is_active,
                },
                metadata_json={
                    "operation": "login",
                },
            )
        )

        await self.uow.commit()

        return token, user

    async def logout(
        self,
        current_user: User,
        session: AuthSession,
    ) -> None:
        """
        Revokes the current authentication session and records a logout audit event.
        """
        session.revoked_at = datetime.now(UTC)

        await self.audit_service.write_audit_entry(
            AuditRecordCreatePayload(
                actor_user_id=current_user.id,
                action_type=AuditActionType.LOGOUT,
                source_context="AUTH_SERVICE",
                entity_type="USER",
                entity_public_id=str(current_user.public_id),
                entity_version=await self.audit_service.get_next_entity_version(
                    entity_type="USER",
                    entity_public_id=str(current_user.public_id),
                ),
                before_snapshot_json={
                    "public_id": str(current_user.public_id),
                    "email": current_user.email,
                    "is_active": current_user.is_active,
                },
                after_snapshot_json={
                    "public_id": str(current_user.public_id),
                    "email": current_user.email,
                    "is_active": current_user.is_active,
                },
                metadata_json={
                    "operation": "logout",
                    "session_public_id": str(session.public_id),
                    "jti": session.jti,
                },
            )
        )

        await self.uow.commit()

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