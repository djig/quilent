from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.middleware.rate_limit import limiter
from app.models import User
from app.schemas.api import (
    LoginRequest,
    OAuthSyncRequest,
    OAuthSyncResponse,
    Token,
    UserCreate,
    UserResponse,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register(
    request: Request, user_data: UserCreate, db: AsyncSession = Depends(get_db)
):
    # Check if user exists
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request, credentials: LoginRequest, db: AsyncSession = Depends(get_db)
):
    """Login with email and password. Returns JWT access token."""
    query = select(User).where(User.email == credentials.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/oauth-sync", response_model=OAuthSyncResponse)
@limiter.limit("20/minute")
async def oauth_sync(
    request: Request, data: OAuthSyncRequest, db: AsyncSession = Depends(get_db)
):
    """
    Sync OAuth user to our database.
    Called by NextAuth after successful OAuth login.
    Creates user if not exists, returns JWT for API calls.
    """
    # Find existing user by email
    query = select(User).where(User.email == data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        # Create new user (no password for OAuth users)
        user = User(
            email=data.email,
            name=data.name,
            hashed_password=None,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif data.name and not user.name:
        # Update name if provided and user doesn't have one
        user.name = data.name
        await db.commit()
        await db.refresh(user)

    # Generate JWT token for API calls
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return OAuthSyncResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
        ),
    )
