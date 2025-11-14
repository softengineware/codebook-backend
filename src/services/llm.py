"""Stub LLM service for MVP."""
from __future__ import annotations

from datetime import datetime
from typing import Any


def analyze_codebook(items: list[dict[str, Any]], rules_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a placeholder analysis for uploaded codebooks.

    This keeps the API contract intact until a real LLM integration is implemented.
    """
    item_count = len(items)
    summary = f"Analyzed {item_count} items using placeholder logic."
    details = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "rule_snapshot": rules_snapshot or {},
        "insights": [
            {
                "type": "structure",
                "message": "Codebook structure looks consistent for initial upload.",
            }
        ],
    }
    return {"analysis_summary": summary, "analysis_details": details}
