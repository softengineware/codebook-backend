"""LLM usage tracking models."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

OperationType = Literal["analysis", "refactor", "search", "recommendation", "other"]


class LLMUsageBase(BaseModel):
    client_id: UUID
    job_id: UUID | None = None
    operation_type: OperationType
    model_name: str
    tokens_input: int = Field(..., ge=0)
    tokens_output: int = Field(..., ge=0)
    tokens_total: int = Field(..., ge=0)
    cost_usd: float = Field(..., ge=0.0)
    latency_ms: int | None = Field(None, ge=0)


class LLMUsageCreate(LLMUsageBase):
    pass


class LLMUsage(LLMUsageBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
