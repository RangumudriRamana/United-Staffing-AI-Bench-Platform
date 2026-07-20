from uuid import UUID
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.enums import Role
from app.auth.security import decode_access_token
from app.auth.service import AuthenticationService
from app.core.exceptions import AppException
from app.database.session import get_db
from app.models.user import User

# Setting up the standard HTTP Bearer security scheme
# This automatically lights up the "Authorize" padlock button in Swagger UI
security_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extracts the JWT from the Authorization header, validates its signature/expiration,
    and resolves the currently active database User record.
    """
    try:
        # Decode the incoming token credentials
        payload = decode_access_token(token.credentials)
        public_id_str = payload.get("sub")
        
        if not public_id_str:
            raise AppException(
                message="Could not validate credentials: subject identifier missing.",
                error_code="UNAUTHORIZED",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        
        public_id = UUID(public_id_str)
        
    except (PyJWTError, ValueError):
        raise AppException(
            message="Could not validate credentials: token is invalid or expired.",
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Use our orchestration service layer to safely pull the user record
    service = AuthenticationService(db)
    user = await service.get_current_user(public_id)
    
    return user


class RequireRole:
    """
    Reusable dependency factory for enforcing Role-Based Access Control (RBAC).
    
    Example Usage:
        @router.get("/admin-dashboard", dependencies=[Depends(RequireRole([Role.ADMIN]))])
    """
    def __init__(self, allowed_roles: list[Role]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise AppException(
                message="Access denied: your profile lacks the necessary permissions.",
                error_code="FORBIDDEN",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return current_user