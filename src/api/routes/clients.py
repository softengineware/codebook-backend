"""Client API routes."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, status

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_client() -> dict:
    """Create a new client (placeholder)."""
    return {
        "message": "Create client endpoint - to be implemented",
        "status": "not_implemented",
    }


@router.get("")
def list_clients(
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """List all clients (placeholder)."""
    return {
        "message": "List clients endpoint - to be implemented",
        "data": [],
        "status": "not_implemented",
    }


@router.get("/{client_id}")
def get_client(
    client_id: UUID,
) -> dict:
    """Get a specific client (placeholder)."""
    return {
        "message": "Get client endpoint - to be implemented",
        "client_id": str(client_id),
        "status": "not_implemented",
    }
