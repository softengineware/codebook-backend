"""Codebook version models."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CodebookVersionBase(BaseModel):
    """Shared fields for codebook versions."""

    label: str | None = Field(None, max_length=255, description="Version label")
    notes: str | None = Field(None, max_length=2000, description="Version notes")
    rules_snapshot: dict[str, Any] | None = Field(None, description="Rules snapshot")
    analysis_summary: str | None = None
    analysis_details: dict[str, Any] | None = None
    prompt_version: str | None = None
    is_active: bool = True
    created_by: str | None = None


class CodebookVersionCreate(CodebookVersionBase):
    """Payload for creating a new version."""

    codebook_id: UUID
    version_number: int = Field(..., gt=0)


class CodebookVersion(CodebookVersionBase):
    """Version as stored in the database."""

    id: UUID
    codebook_id: UUID
    version_number: int
    created_at: datetime

    model_config = {"from_attributes": True}
