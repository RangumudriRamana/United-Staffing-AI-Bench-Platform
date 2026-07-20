from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    AuthUser,
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.auth.service import AuthenticationService
from app.core.responses import ApiResponse
from app.database.session import get_db
from app.models.user import User

router = APIRouter()


@router.post(
    "/register",
    response_model=ApiResponse[RegisterResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Exposes the public registration endpoint to create new user accounts.
    """
    service = AuthenticationService(db)
    user = await service.register(request)
    return ApiResponse(
        success=True,
        message="User registered successfully.",
        data=RegisterResponse(user=AuthUser.model_validate(user)),
    )


@router.post(
    "/login",
    response_model=ApiResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthenticationService(db)
    
    # Now this will correctly receive the (token, user) pair
    token, user = await service.login(request)

    return ApiResponse(
        success=True,
        message="Login successful.",
        data=LoginResponse(
            access_token=token,
            # Now 'user' is the actual database object, not the letter 'y'
            user=AuthUser.model_validate(user),
        ),
    )


@router.get(
    "/me",
    response_model=ApiResponse[CurrentUserResponse],
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the profile details of the securely authenticated user session.
    Guarded by the JWT verification dependency.
    """
    return ApiResponse(
        success=True,
        message="Current user profile retrieved successfully.",
        data=CurrentUserResponse(user=AuthUser.model_validate(current_user)),
    )