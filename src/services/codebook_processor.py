"""Codebook processing orchestration service."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.codebook import CodebookCreate
from src.models.version import CodebookVersionCreate
from src.repositories.codebook_items import CodebookItemRepository
from src.repositories.codebook_versions import CodebookVersionRepository
from src.repositories.codebooks import CodebookRepository
from src.repositories.jobs import JobRepository
from src.services.llm import LLMService

logger = logging.getLogger(__name__)


class CodebookProcessor:
    """Orchestrates the codebook upload-to-analysis pipeline."""

    def __init__(self, db: SupabaseClient) -> None:
        self._db = db
        self._codebook_repo = CodebookRepository(db)
        self._version_repo = CodebookVersionRepository(db)
        self._item_repo = CodebookItemRepository(db)
        self._job_repo = JobRepository(db)
        self._llm = LLMService()

    def process_upload(
        self,
        job_id: UUID,
        client_id: UUID,
        codebook_name: str,
        codebook_type: str,
        description: str | None,
        items: list[dict[str, Any]],
    ) -> None:
        """Process an uploaded codebook: create records, analyze with LLM, store results.

        This runs as a background task. Updates the job record with progress.
        """
        try:
            # Mark job as running
            self._job_repo.update_job(job_id, status="running", progress=5)
            logger.info(f"Processing upload job {job_id}: {len(items)} items")

            # Step 1: Create codebook
            codebook = self._codebook_repo.create_codebook(
                client_id=client_id,
                data=CodebookCreate(
                    name=codebook_name,
                    type=codebook_type,
                    description=description,
                ),
            )
            self._job_repo.update_job(job_id, progress=15)
            logger.info(f"Created codebook {codebook.id}")

            # Update job with codebook_id
            self._db.table("jobs").update(
                {"codebook_id": str(codebook.id)}
            ).eq("id", str(job_id)).execute()

            # Step 2: Create version 1
            version = self._version_repo.create_version(
                CodebookVersionCreate(
                    codebook_id=codebook.id,
                    version_number=1,
                    label="Initial import",
                    notes=f"Imported {len(items)} items from uploaded file",
                )
            )
            self._job_repo.update_job(job_id, progress=25)
            logger.info(f"Created version {version.id} (v1)")

            # Step 3: Analyze with LLM
            self._job_repo.update_job(job_id, progress=30)
            llm_result = self._llm.analyze_and_code_items(
                items=items,
                codebook_type=codebook_type,
            )
            self._job_repo.update_job(job_id, progress=70)
            logger.info(f"LLM analysis complete: {len(llm_result.get('items', []))} items coded")

            # Step 4: Build and insert codebook items
            llm_items = llm_result.get("items", [])
            db_items = self._build_item_records(
                llm_items=llm_items,
                original_items=items,
                version_id=version.id,
                client_id=client_id,
            )

            if db_items:
                self._item_repo.bulk_insert_items(db_items)
            self._job_repo.update_job(job_id, progress=85)
            logger.info(f"Inserted {len(db_items)} items into database")

            # Step 5: Update version with analysis
            self._db.table("codebook_versions").update({
                "analysis_summary": llm_result.get("analysis_summary"),
                "analysis_details": llm_result.get("analysis_details"),
                "prompt_version": "analysis_v1.0",
            }).eq("id", str(version.id)).execute()

            # Step 6: Mark job completed
            self._job_repo.update_job(
                job_id,
                status="completed",
                progress=100,
                result_payload={
                    "codebook_id": str(codebook.id),
                    "version_id": str(version.id),
                    "item_count": len(db_items),
                    "analysis_summary": llm_result.get("analysis_summary"),
                },
            )

            # Update completed_at
            self._db.table("jobs").update({
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", str(job_id)).execute()

            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            self._job_repo.update_job(
                job_id,
                status="failed",
                error=str(e),
            )

    def _build_item_records(
        self,
        llm_items: list[dict[str, Any]],
        original_items: list[dict[str, Any]],
        version_id: UUID,
        client_id: UUID,
    ) -> list[dict[str, Any]]:
        """Build database-ready item records from LLM output."""
        records = []

        # Build a lookup from original_label for merging
        original_lookup: dict[str, dict[str, Any]] = {}
        for item in original_items:
            label = item.get("original_label", "").strip().lower()
            if label:
                original_lookup[label] = item

        seen_codes: set[str] = set()

        for i, llm_item in enumerate(llm_items):
            code = llm_item.get("code", f"UNCLASSIFIED-{i+1:04d}")

            # Ensure unique codes within this version
            base_code = code
            counter = 1
            while code in seen_codes:
                code = f"{base_code}-{counter}"
                counter += 1
            seen_codes.add(code)

            original_label = llm_item.get("original_label", f"Item {i+1}")

            # Merge with original item data if available
            orig = original_lookup.get(original_label.strip().lower(), {})

            # Validate application value
            application = llm_item.get("application") or orig.get("application")
            valid_apps = {"sanitary_sewer", "storm_sewer", "water", "other"}
            if application and application not in valid_apps:
                application = "other"

            record = {
                "version_id": str(version_id),
                "client_id": str(client_id),
                "original_label": original_label,
                "description": llm_item.get("description") or orig.get("description"),
                "code": code,
                "application": application,
                "csi_division": llm_item.get("csi_division"),
                "csi_section": llm_item.get("csi_section"),
                "metadata": llm_item.get("metadata") or orig.get("metadata"),
            }
            records.append(record)

        return records
