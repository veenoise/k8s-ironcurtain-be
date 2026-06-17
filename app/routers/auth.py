from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import create_access_token, hash_password, verify_password
from app.database import db
from app.dependencies import get_current_user
from app.schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    existing = await db.user.find_unique(where={"username": body.username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    await db.user.create(
        data={
            "username": body.username,
            "passwordHash": hash_password(body.password),
        },
    )
    return {"message": "Operative registered successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = await db.user.find_unique(where={"username": body.username})
    if not user or not verify_password(body.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(user.username, role=user.role)
    return TokenResponse(access_token=token)


@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    return {"message": "Logged out successfully"}
