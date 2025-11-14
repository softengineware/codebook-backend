"""Repository layer for prompt templates."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.prompt_template import PromptTemplate, PromptTemplateCreate, TemplateName


class PromptTemplateRepository:
    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def create_template(self, data: PromptTemplateCreate) -> PromptTemplate:
        payload = data.model_dump()
        result = (
            self._db.table("prompt_templates")
            .insert(payload)
            .select("*")
            .single()
            .execute()
        )
        return PromptTemplate.model_validate(result.data)

    def get_template(self, template_id: UUID) -> Optional[PromptTemplate]:
        result = (
            self._db.table("prompt_templates")
            .select("*")
            .eq("id", str(template_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return PromptTemplate.model_validate(result.data)

    def list_templates(
        self,
        template_name: TemplateName | None = None,
        active_only: bool = False,
    ) -> list[PromptTemplate]:
        query = (
            self._db.table("prompt_templates")
            .select("*")
            .order("created_at", desc=True)
        )
        if template_name:
            query = query.eq("template_name", template_name)
        if active_only:
            query = query.eq("is_active", True)

        result = query.execute()
        return [PromptTemplate.model_validate(row) for row in result.data or []]

    def deactivate_template(self, template_id: UUID) -> None:
        self._db.table("prompt_templates").update({"is_active": False}).eq("id", str(template_id)).execute()
