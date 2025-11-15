"""Authentication routes."""
from fastapi import APIRouter, status

router = APIRouter(prefix="/auth")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login() -> dict:
    """User login endpoint (placeholder)."""
    return {
        "message": "Authentication endpoint - to be implemented",
        "status": "not_implemented",
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout() -> dict:
    """User logout endpoint (placeholder)."""
    return {
        "message": "Logout endpoint - to be implemented",
        "status": "not_implemented",
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token() -> dict:
    """Token refresh endpoint (placeholder)."""
    return {
        "message": "Token refresh endpoint - to be implemented",
        "status": "not_implemented",
    }
