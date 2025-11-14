"""Repository layer for codebook rules."""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.rule import CodebookRule, CodebookRuleCreate, CodebookRuleUpdate


class CodebookRuleRepository:
    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def create_rule(self, data: CodebookRuleCreate) -> CodebookRule:
        payload = data.model_dump()
        result = (
            self._db.table("codebook_rules")
            .insert(payload)
            .select("*")
            .single()
            .execute()
        )
        return CodebookRule.model_validate(result.data)

    def get_rule(self, rule_id: UUID) -> Optional[CodebookRule]:
        result = (
            self._db.table("codebook_rules")
            .select("*")
            .eq("id", str(rule_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return CodebookRule.model_validate(result.data)

    def list_rules(
        self,
        client_id: UUID,
        codebook_id: UUID | None = None,
        active_only: bool = False,
    ) -> list[CodebookRule]:
        query = (
            self._db.table("codebook_rules")
            .select("*")
            .eq("client_id", str(client_id))
            .order("created_at", desc=True)
        )
        if codebook_id:
            query = query.eq("codebook_id", str(codebook_id))
        if active_only:
            query = query.eq("is_active", True)

        result = query.execute()
        return [CodebookRule.model_validate(row) for row in result.data or []]

    def update_rule(self, rule_id: UUID, data: CodebookRuleUpdate) -> Optional[CodebookRule]:
        payload = {k: v for k, v in data.model_dump(exclude_none=True).items()}
        if not payload:
            return self.get_rule(rule_id)

        result = (
            self._db.table("codebook_rules")
            .update(payload)
            .eq("id", str(rule_id))
            .select("*")
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return CodebookRule.model_validate(result.data)

    def deactivate_rule(self, rule_id: UUID) -> None:
        self._db.table("codebook_rules").update({"is_active": False}).eq("id", str(rule_id)).execute()
