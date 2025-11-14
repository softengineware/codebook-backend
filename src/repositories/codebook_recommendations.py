"""Repository layer for codebook recommendations."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.recommendation import Recommendation, RecommendationCreate, RecommendationStatus


class RecommendationRepository:
    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def create_recommendation(self, data: RecommendationCreate) -> Recommendation:
        payload = data.model_dump()
        result = (
            self._db.table("codebook_recommendations")
            .insert(payload)
            .select("*")
            .single()
            .execute()
        )
        return Recommendation.model_validate(result.data)

    def get_recommendation(self, recommendation_id: UUID) -> Optional[Recommendation]:
        result = (
            self._db.table("codebook_recommendations")
            .select("*")
            .eq("id", str(recommendation_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return Recommendation.model_validate(result.data)

    def list_recommendations(
        self,
        version_id: UUID,
        status: RecommendationStatus | None = None,
        limit: int = 50,
    ) -> list[Recommendation]:
        query = (
            self._db.table("codebook_recommendations")
            .select("*")
            .eq("version_id", str(version_id))
            .order("created_at", desc=True)
            .limit(limit)
        )
        if status:
            query = query.eq("status", status)

        result = query.execute()
        return [Recommendation.model_validate(row) for row in result.data or []]

    def update_status(
        self,
        recommendation_id: UUID,
        status: RecommendationStatus,
        acted_by: str | None = None,
    ) -> Optional[Recommendation]:
        payload: dict[str, object] = {"status": status}
        if acted_by:
            payload["acted_by"] = acted_by

        result = (
            self._db.table("codebook_recommendations")
            .update(payload)
            .eq("id", str(recommendation_id))
            .select("*")
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return Recommendation.model_validate(result.data)
