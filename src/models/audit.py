"""Audit log models."""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

AuditAction = Literal[
    "initial_import",
    "rule_update",
    "version_created",
    "recommendation_applied",
    "revert",
    "items_added",
    "items_updated",
    "refactor_started",
    "refactor_completed",
]


class AuditEntryBase(BaseModel):
    action_type: AuditAction
    summary: str = Field(..., min_length=1)
    details: dict[str, Any] | None = None
    performed_by: str | None = None
    llm_tokens_used: int | None = None


class AuditEntryCreate(AuditEntryBase):
    client_id: UUID
    codebook_id: UUID | None = None
    version_id: UUID | None = None


class AuditEntry(AuditEntryBase):
    id: UUID
    client_id: UUID
    codebook_id: UUID | None = None
    version_id: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
