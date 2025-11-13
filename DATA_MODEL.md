# Data Model – Supabase (SQL)

This is a suggested schema for Supabase/PostgreSQL. Names can be adjusted by the implementing engineer.

---

## 1. `clients`

Basic tenant-level partitioning.

- `id` (uuid, pk)
- `name` (text, not null)
- `slug` (text, unique, optional)
- `contact_email` (text, optional)
- `metadata` (jsonb, optional)
- `created_at` (timestamptz, default now())
- `updated_at` (timestamptz, default now())
- `deleted_at` (timestamptz, nullable) — soft delete

Indexes:
- `slug` (unique where deleted_at IS NULL)
- `(deleted_at)` for filtering active clients

---

## 2. `codebooks`

Logical grouping of versions for a specific client and type.

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id ON DELETE CASCADE)
- `name` (text, not null)
- `type` (text, not null) — enum-like: `material`, `activity`, `bid_item`
- `description` (text, optional)
- `locked_by` (text or uuid, optional) — prevents concurrent modifications
- `locked_at` (timestamptz, optional) — timestamp of lock
- `created_at` (timestamptz, default now())
- `updated_at` (timestamptz, default now())
- `deleted_at` (timestamptz, nullable) — soft delete

**Note:** To find the active version, query `codebook_versions` for `MAX(version_number) WHERE codebook_id = ? AND is_active = true`. This avoids circular FK dependency with `codebook_versions`.

Indexes:
- `(client_id, type)`
- `(client_id, deleted_at)` for filtering active codebooks

Constraints:
- `CHECK (type IN ('material', 'activity', 'bid_item'))`
- `UNIQUE (client_id, name, type) WHERE deleted_at IS NULL` — prevents duplicate codebook names per client

---

## 3. `codebook_versions`

Each version is a full snapshot of items under specific rules/structure.

- `id` (uuid, pk)
- `codebook_id` (uuid, fk -> codebooks.id ON DELETE CASCADE)
- `version_number` (int, not null) — monotonically increasing per codebook
- `label` (text, optional, e.g. "Initial import", "Post-refactor 1")
- `notes` (text, optional)
- `rules_snapshot` (jsonb) — snapshot of rules used to generate this version
- `analysis_summary` (text, optional)
- `analysis_details` (jsonb, optional) — structured findings from LLM
- `prompt_version` (text, optional) — e.g. "analysis_v2.1" to track which prompt generated this
- `is_active` (boolean, default true) — marks the currently active version
- `created_by` (text or uuid, optional)
- `created_at` (timestamptz, default now())

Indexes:
- `(codebook_id, version_number)` unique
- `(codebook_id, is_active)` for quickly finding active version

Constraints:
- `CHECK (version_number > 0)`

---

## 4. `codebook_items`

Items in a specific version.

- `id` (uuid, pk)
- `version_id` (uuid, fk -> codebook_versions.id ON DELETE CASCADE)
- `client_id` (uuid, fk -> clients.id ON DELETE CASCADE) — denormalized for convenience
- `original_label` (text, not null) — raw label from upload
- `description` (text, optional)
- `code` (text, not null) — generated or existing code (e.g. `2-DIP-08-B`)
- `application` (text, optional) — e.g. sanitary_sewer, storm_sewer, water
- `csi_division` (text, optional) — e.g. "33" for Utilities
- `csi_section` (text, optional) — e.g. "33 30 00" for Sanitary Sewerage
- `metadata` (jsonb, optional) — diameter, material, class, etc.
- `created_at` (timestamptz, default now())

Indexes:
- `(client_id, version_id)`
- `(version_id, code)` — for quick lookup within a version
- `(code, client_id)` — for searching across versions
- `(csi_division, csi_section)` — for CSI-based queries
- `(application)` — for application filtering

Constraints:
- `UNIQUE (version_id, code)` — codes must be unique within a version
- `CHECK (application IN ('sanitary_sewer', 'storm_sewer', 'water', 'other') OR application IS NULL)`

---

## 5. `codebook_rules`

Rules/preferences controlling how codes are generated & organized.

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id ON DELETE CASCADE)
- `codebook_id` (uuid, fk -> codebooks.id ON DELETE CASCADE, nullable) — null = global for client
- `name` (text, not null)
- `is_active` (boolean, default true)
- `rules_json` (jsonb, not null) — e.g.
  - ordering strategy (material-first, diameter-first, CSI-first)
  - naming templates (e.g. `"${family}-${material}-${diameter}-${type_code}"`)
  - grouping rules (application, division, etc.)
- `created_at` (timestamptz, default now())
- `updated_at` (timestamptz, default now())

Indexes:
- `(client_id, is_active)`
- `(codebook_id, is_active)` for codebook-specific rules

Constraints:
- `CHECK (jsonb_typeof(rules_json) = 'object')` — ensure rules_json is a valid object

---

## 6. `codebook_recommendations`

LLM-generated suggestions tied to a version.

- `id` (uuid, pk)
- `version_id` (uuid, fk -> codebook_versions.id ON DELETE CASCADE)
- `client_id` (uuid, fk -> clients.id ON DELETE CASCADE)
- `item_id` (uuid, fk -> codebook_items.id ON DELETE CASCADE, nullable) — null if global suggestion
- `category` (text, not null) — e.g. `csi_mapping`, `naming`, `grouping`, `missing_item`
- `suggestion` (text, not null)
- `suggestion_payload` (jsonb) — structured change instructions
- `status` (text, default 'pending') — `pending`, `accepted`, `rejected`, `dismissed`
- `created_at` (timestamptz, default now())
- `updated_at` (timestamptz, default now())
- `acted_by` (text or uuid, optional)

Indexes:
- `(version_id, status)` for filtering recommendations by status
- `(client_id, status, created_at)` for client-wide recommendation views
- `(item_id)` for item-specific recommendations

Constraints:
- `CHECK (status IN ('pending', 'accepted', 'rejected', 'dismissed'))`
- `CHECK (category IN ('csi_mapping', 'naming', 'grouping', 'missing_item', 'inconsistency', 'other'))`

---

## 7. `audit_log`

Records every significant change for traceability.

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id ON DELETE CASCADE)
- `codebook_id` (uuid, fk -> codebooks.id ON DELETE SET NULL, nullable)
- `version_id` (uuid, fk -> codebook_versions.id ON DELETE SET NULL, nullable)
- `action_type` (text, not null) — e.g. `initial_import`, `rule_update`, `version_created`, `recommendation_applied`, `revert`
- `performed_by` (text or uuid, nullable)
- `summary` (text, not null)
- `details` (jsonb) — before/after diffs, rule IDs, etc.
- `llm_tokens_used` (int, optional) — track token usage per action
- `created_at` (timestamptz, default now())

Indexes:
- `(client_id, created_at DESC)` for recent activity queries
- `(client_id, codebook_id, created_at DESC)` for codebook-specific history
- `(action_type, client_id, created_at)` for filtering by action type

Constraints:
- `CHECK (action_type IN ('initial_import', 'rule_update', 'version_created', 'recommendation_applied', 'revert', 'items_added', 'items_updated', 'refactor_started', 'refactor_completed'))`

---

## 8. `jobs`

Track async operations (LLM analysis, refactoring, large uploads).

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id ON DELETE CASCADE)
- `codebook_id` (uuid, fk -> codebooks.id ON DELETE SET NULL, nullable)
- `job_type` (text, not null) — e.g. `initial_analysis`, `refactor`, `bulk_upload`
- `status` (text, default 'pending') — `pending`, `running`, `completed`, `failed`, `cancelled`
- `progress` (int, default 0) — percentage 0-100
- `result` (jsonb, nullable) — job output/results
- `error` (text, nullable) — error message if failed
- `started_at` (timestamptz, nullable)
- `completed_at` (timestamptz, nullable)
- `created_at` (timestamptz, default now())
- `created_by` (text or uuid, nullable)

Indexes:
- `(client_id, status, created_at DESC)` for active job monitoring
- `(status, started_at)` for processing queue

Constraints:
- `CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))`
- `CHECK (job_type IN ('initial_analysis', 'refactor', 'bulk_upload', 'semantic_search', 'export'))`
- `CHECK (progress BETWEEN 0 AND 100)`

---

## 9. `prompt_templates`

Version and track LLM prompt templates.

- `id` (uuid, pk)
- `template_name` (text, not null) — e.g. `initial_analysis`, `refactor`, `recommendation`
- `version` (text, not null) — e.g. `v1.0`, `v2.1`
- `template_text` (text, not null) — the actual prompt template
- `variables` (jsonb) — list of variables used in template
- `is_active` (boolean, default true)
- `created_at` (timestamptz, default now())
- `created_by` (text or uuid, nullable)

Indexes:
- `(template_name, version)` unique
- `(template_name, is_active)` for finding active templates

Constraints:
- `CHECK (template_name IN ('initial_analysis', 'refactor', 'recommendation', 'csi_mapping', 'code_generation'))`

---

## 10. `llm_usage`

Track LLM API usage and costs per client.

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id ON DELETE CASCADE)
- `job_id` (uuid, fk -> jobs.id ON DELETE SET NULL, nullable)
- `operation_type` (text, not null) — e.g. `analysis`, `refactor`, `search`
- `model_name` (text, not null) — e.g. `gpt-4o`, `claude-3-5-sonnet`
- `tokens_input` (int, not null)
- `tokens_output` (int, not null)
- `tokens_total` (int, not null)
- `cost_usd` (numeric(10, 6), not null) — calculated cost
- `latency_ms` (int, nullable) — response time
- `created_at` (timestamptz, default now())

Indexes:
- `(client_id, created_at)` for usage reports
- `(created_at)` for global usage analytics

Constraints:
- `CHECK (tokens_total = tokens_input + tokens_output)`
- `CHECK (cost_usd >= 0)`

---

## 11. Vector Metadata (optional tables)

Pinecone will hold the actual vectors, but you may want a local index:

### `item_embeddings`

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id ON DELETE CASCADE)
- `item_id` (uuid, fk -> codebook_items.id ON DELETE CASCADE)
- `pinecone_id` (text, not null) — ID used in Pinecone
- `embedding_model` (text) — e.g. `text-embedding-3-large`
- `created_at` (timestamptz, default now())

Indexes:
- `(item_id)` unique
- `(pinecone_id)` unique

### `csi_embeddings`

- `id` (uuid, pk)
- `client_id` (uuid, nullable) — global if null
- `csi_code` (text, not null) — e.g. "33", "33 30 00"
- `csi_title` (text, not null)
- `csi_description` (text, optional)
- `pinecone_id` (text, not null)
- `embedding_model` (text)
- `created_at` (timestamptz, default now())

Indexes:
- `(csi_code)` unique
- `(pinecone_id)` unique

---

## Summary of Cascade Behaviors

- **Client deleted** → All codebooks, rules, items, recommendations, audit logs, jobs, and LLM usage CASCADE deleted
- **Codebook deleted** → All versions, items, rules, and recommendations CASCADE deleted
- **Version deleted** → All items and recommendations CASCADE deleted
- **Item deleted** → Recommendations for that item CASCADE deleted
- **Audit log** → Uses SET NULL for codebook/version FKs to preserve history even if source is deleted

---

This layout is intentionally flexible; the implementing engineer can optimize and normalize
further as needed.
