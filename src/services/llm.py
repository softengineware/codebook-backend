"""LLM service for codebook analysis and code generation."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from src.core.config import settings
from src.core.errors import LLMAPIError

logger = logging.getLogger(__name__)

# CSI MasterFormat divisions relevant to civil construction
CSI_CONTEXT = """
Key CSI MasterFormat Divisions for Civil Construction:
- Division 02: Existing Conditions (site assessment, demolition)
- Division 31: Earthwork (grading, excavation, fill, soil stabilization)
- Division 32: Exterior Improvements (paving, curbs, sidewalks, fencing, landscaping)
- Division 33: Utilities (water, sanitary sewer, storm sewer, gas, electrical)
  - 33 05 00: Common Work Results for Utilities
  - 33 10 00: Water Utilities (water distribution, water mains, valves, hydrants)
  - 33 30 00: Sanitary Sewerage (sanitary sewer piping, manholes, cleanouts)
  - 33 40 00: Storm Drainage (storm sewer piping, inlets, detention)
  - 33 50 00: Fuel Distribution
  - 33 70 00: Electrical Utilities
- Division 34: Transportation (roadways, signals, signage)
- Division 35: Waterway and Marine Construction
"""

ANALYSIS_PROMPT = """You are an expert construction materials classifier and CSI MasterFormat specialist.

{csi_context}

Given these {codebook_type} items from a civil construction codebook, for EACH item:
1. Generate a standardized code using this pattern: {{FAMILY_DIGIT}}-{{MATERIAL_ABBR}}-{{SIZE}}-{{TYPE_CODE}}
   - FAMILY_DIGIT: 1=Earthwork, 2=Pipe, 3=Fitting, 4=Valve, 5=Structure, 6=Electrical, 7=Paving, 8=Other
   - MATERIAL_ABBR: DIP=Ductile Iron, PVC=PVC, HDPE=HDPE, RCP=Reinforced Concrete, CMP=Corrugated Metal, STL=Steel, CIP=Cast Iron, etc.
   - SIZE: diameter or size in inches (e.g., 08, 12, 24), use 00 if not applicable
   - TYPE_CODE: P=Pipe, B=Bend, T=Tee, V=Valve, G=Gate, M=Manhole, H=Hydrant, C=Coupling, R=Reducer, E=Elbow, etc.
   Example: 2-DIP-08-B = 8" Ductile Iron Pipe Bend, 4-DIP-06-G = 6" DIP Gate Valve
2. Assign the correct CSI MasterFormat division (e.g., "33")
3. Assign the CSI section (e.g., "33 30 00")
4. Categorize by application: sanitary_sewer, storm_sewer, water, or other
5. Write a clear, standardized description
6. Extract metadata (diameter, material, type, class, etc.)

Items to analyze:
{items_json}

Return valid JSON with this exact structure:
{{
  "items": [
    {{
      "original_label": "the exact original label provided",
      "code": "generated code",
      "description": "standardized description",
      "csi_division": "two digit division number",
      "csi_section": "full section code like 33 30 00",
      "application": "sanitary_sewer|storm_sewer|water|other",
      "metadata": {{"diameter": "...", "material": "...", "type": "...", "class": "..."}}
    }}
  ],
  "analysis_summary": "2-3 sentence summary of codebook quality and composition",
  "analysis_details": {{
    "total_items": 0,
    "divisions_found": ["33", "32"],
    "applications_breakdown": {{"water": 0, "sanitary_sewer": 0, "storm_sewer": 0, "other": 0}},
    "recommendations": ["recommendation 1", "recommendation 2"]
  }}
}}
"""


class LLMService:
    """Service for LLM-powered codebook analysis."""

    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.LLM_API_KEY)
        self._model = settings.LLM_MODEL_NAME

    def analyze_and_code_items(
        self,
        items: list[dict[str, Any]],
        codebook_type: str,
        rules: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze items and generate standardized codes via LLM.

        For large item lists, processes in batches of 100.
        """
        if len(items) <= 100:
            return self._analyze_batch(items, codebook_type, rules)

        # Batch processing for large codebooks
        all_items: list[dict[str, Any]] = []
        batch_size = 100

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}/{(len(items) + batch_size - 1) // batch_size}")
            result = self._analyze_batch(batch, codebook_type, rules)
            all_items.extend(result.get("items", []))

        # Generate a final summary for the full codebook
        summary_result = self._generate_summary(all_items, codebook_type)

        return {
            "items": all_items,
            "analysis_summary": summary_result.get("analysis_summary", f"Analyzed {len(all_items)} {codebook_type} items."),
            "analysis_details": summary_result.get("analysis_details", {"total_items": len(all_items)}),
        }

    def _analyze_batch(
        self,
        items: list[dict[str, Any]],
        codebook_type: str,
        rules: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze a single batch of items."""
        # Prepare items for the prompt (only send relevant fields)
        items_for_prompt = []
        for item in items:
            entry: dict[str, Any] = {"original_label": item.get("original_label", "")}
            if item.get("description"):
                entry["description"] = item["description"]
            if item.get("metadata"):
                entry["metadata"] = item["metadata"]
            if item.get("application"):
                entry["application"] = item["application"]
            items_for_prompt.append(entry)

        prompt = ANALYSIS_PROMPT.format(
            csi_context=CSI_CONTEXT,
            codebook_type=codebook_type,
            items_json=json.dumps(items_for_prompt, indent=2),
        )

        if rules:
            prompt += f"\n\nAdditional coding rules to follow:\n{json.dumps(rules, indent=2)}"

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "You are a construction codebook specialist. Always return valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=4096,
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)

            # Validate structure
            if "items" not in result:
                result["items"] = []

            logger.info(
                f"LLM analysis complete",
                extra={
                    "items_sent": len(items),
                    "items_returned": len(result.get("items", [])),
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                },
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            raise LLMAPIError(
                provider=settings.LLM_PROVIDER,
                error_code="INVALID_JSON",
                error_message=f"LLM returned invalid JSON: {str(e)}",
            )
        except Exception as e:
            logger.error(f"LLM API error: {e}", exc_info=True)
            raise LLMAPIError(
                provider=settings.LLM_PROVIDER,
                error_code="API_ERROR",
                error_message=str(e),
            )

    def _generate_summary(
        self, all_items: list[dict[str, Any]], codebook_type: str
    ) -> dict[str, Any]:
        """Generate a summary analysis for the full codebook after batch processing."""
        divisions = list(set(item.get("csi_division", "") for item in all_items if item.get("csi_division")))
        apps: dict[str, int] = {}
        for item in all_items:
            app = item.get("application", "other") or "other"
            apps[app] = apps.get(app, 0) + 1

        return {
            "analysis_summary": f"Analyzed {len(all_items)} {codebook_type} items across {len(divisions)} CSI divisions.",
            "analysis_details": {
                "total_items": len(all_items),
                "divisions_found": divisions,
                "applications_breakdown": apps,
                "recommendations": [],
            },
        }


def get_llm_service() -> LLMService:
    """Factory function for dependency injection."""
    return LLMService()
