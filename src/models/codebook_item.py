"""Codebook item models."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CodebookItemBase(BaseModel):
    """Shared fields for codebook items."""

    original_label: str = Field(..., min_length=1)
    description: str | None = None
    code: str = Field(..., min_length=1)
    application: str | None = Field(
        None,
        description="Application category (sanitary_sewer, storm_sewer, water, other)",
    )
    csi_division: str | None = None
    csi_section: str | None = None
    metadata: dict[str, Any] | None = None


class CodebookItemCreate(CodebookItemBase):
    """Payload for inserting an item."""

    version_id: UUID
    client_id: UUID


class CodebookItem(CodebookItemBase):
    """Item as stored in the database."""

    id: UUID
    version_id: UUID
    client_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
