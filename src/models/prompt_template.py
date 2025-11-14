"""Prompt template models."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

TemplateName = Literal[
    "initial_analysis",
    "refactor",
    "recommendation",
    "csi_mapping",
    "code_generation",
]


class PromptTemplateBase(BaseModel):
    template_name: TemplateName
    version: str = Field(..., min_length=1)
    template_text: str = Field(..., min_length=1)
    variables: dict[str, str] | None = None
    is_active: bool = True
    created_by: str | None = None


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplate(PromptTemplateBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
