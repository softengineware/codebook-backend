"""Codebook recommendation models."""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

RecommendationCategory = Literal[
    "csi_mapping",
    "naming",
    "grouping",
    "missing_item",
    "inconsistency",
    "other",
]
RecommendationStatus = Literal["pending", "accepted", "rejected", "dismissed"]


class RecommendationBase(BaseModel):
    category: RecommendationCategory
    suggestion: str = Field(..., min_length=1)
    suggestion_payload: dict[str, Any] | None = None
    status: RecommendationStatus = "pending"
    acted_by: str | None = None


class RecommendationCreate(RecommendationBase):
    version_id: UUID
    client_id: UUID
    item_id: UUID | None = None


class Recommendation(RecommendationBase):
    id: UUID
    version_id: UUID
    client_id: UUID
    item_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
