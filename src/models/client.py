"""Client data models."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ClientBase(BaseModel):
    """Base client model with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Client name")
    slug: str | None = Field(None, max_length=100, description="URL-friendly identifier")
    contact_email: str | None = Field(None, description="Primary contact email")
    metadata: dict[str, Any] | None = Field(None, description="Additional client metadata")


class ClientCreate(ClientBase):
    """Model for creating a new client."""
    pass


class ClientUpdate(BaseModel):
    """Model for updating a client (partial updates allowed)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=100)
    contact_email: str | None = None
    metadata: dict[str, Any] | None = None


class Client(ClientBase):
    """Complete client model with database fields."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class ClientList(BaseModel):
    """Paginated list of clients."""

    data: list[Client]
    pagination: dict[str, Any]
