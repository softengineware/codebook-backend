"""Client API routes."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.auth import AdminDep, AuthDep
from src.core.errors import ResourceNotFoundError
from src.models.client import ClientCreate
from src.repositories.clients import ClientRepository
from src.services.database import get_supabase_client

router = APIRouter(prefix="/clients", tags=["Clients"])


def get_client_repository(db=Depends(get_supabase_client)) -> ClientRepository:
    return ClientRepository(db)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    repo: Annotated[ClientRepository, Depends(get_client_repository)],
    _: AdminDep,
) -> dict:
    client = repo.create_client(payload)
    return {"data": client}


@router.get("")
def list_clients(
    limit: int = Query(50, ge=1, le=200),
    repo: Annotated[ClientRepository, Depends(get_client_repository)],
    _: AdminDep,
) -> dict:
    return repo.list_clients(limit=limit)


@router.get("/{client_id}")
def get_client(
    client_id: UUID,
    repo: Annotated[ClientRepository, Depends(get_client_repository)],
    auth: AuthDep,
) -> dict:
    client = repo.get_client(client_id)
    if not client:
        raise ResourceNotFoundError("client", str(client_id))

    auth.require_client_access(str(client_id))
    return {"data": client}
