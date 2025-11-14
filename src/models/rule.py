"""Codebook rule models."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CodebookRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True
    rules_json: dict[str, Any]


class CodebookRuleCreate(CodebookRuleBase):
    client_id: UUID
    codebook_id: UUID | None = None


class CodebookRuleUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    rules_json: dict[str, Any] | None = None


class CodebookRule(CodebookRuleBase):
    id: UUID
    client_id: UUID
    codebook_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
