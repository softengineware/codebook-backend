"""Codebook data models."""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


CodebookType = Literal["material", "activity", "bid_item"]


class CodebookBase(BaseModel):
    """Base codebook model."""

    name: str = Field(..., min_length=1, max_length=255, description="Codebook name")
    type: CodebookType = Field(..., description="Codebook type")
    description: str | None = Field(None, max_length=2000, description="Codebook description")


class CodebookCreate(CodebookBase):
    """Model for creating a new codebook."""
    pass


class CodebookUpdate(BaseModel):
    """Model for updating a codebook."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)


class Codebook(CodebookBase):
    """Complete codebook model."""

    id: UUID
    client_id: UUID
    locked_by: str | None = None
    locked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class CodebookWithActiveVersion(Codebook):
    """Codebook with active version information."""

    active_version: dict[str, Any] | None = None


class CodebookUploadRequest(CodebookBase):
    """Model for uploading a new codebook with items."""

    items: list[dict[str, Any]] = Field(..., min_length=1, description="List of codebook items")


class CodebookUploadResponse(BaseModel):
    """Response for codebook upload (async job)."""

    job_id: UUID
    status: str
    message: str
