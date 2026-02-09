"""Authentication routes."""
from fastapi import APIRouter

from src.api.dependencies.auth import AuthDep

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
def get_current_user(auth: AuthDep) -> dict:
    return {
        "data": {
            "client_id": auth.client_id,
            "role": auth.role,
            "user_id": auth.user_id,
        }
    }
