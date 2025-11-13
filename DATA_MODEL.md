# Data Model – Supabase (SQL)

This is a suggested schema for Supabase/PostgreSQL. Names can be adjusted by the implementing engineer.

---

## 1. `clients`

Basic tenant-level partitioning.

- `id` (uuid, pk)
- `name` (text)
- `slug` (text, unique, optional)
- `contact_email` (text, optional)
- `metadata` (jsonb, optional)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)

---

## 2. `codebooks`

Logical grouping of versions for a specific client and type.

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id)
- `name` (text)
- `type` (text) — enum-like: `material`, `activity`, `bid_item`
- `description` (text, optional)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `active_version_id` (uuid, fk -> codebook_versions.id, nullable)

Indexes:
- `(client_id, type)`

---

## 3. `codebook_versions`

Each version is a full snapshot of items under specific rules/structure.

- `id` (uuid, pk)
- `codebook_id` (uuid, fk -> codebooks.id)
- `version_number` (int) — monotonically increasing per codebook
- `label` (text, optional, e.g. "Initial import", "Post-refactor 1")
- `notes` (text, optional)
- `rules_snapshot` (jsonb) — snapshot of rules used to generate this version
- `analysis_summary` (text, optional)
- `analysis_details` (jsonb, optional) — structured findings from LLM
- `created_by` (text or uuid, optional)
- `created_at` (timestamptz)

Indexes:
- `(codebook_id, version_number)` unique

---

## 4. `codebook_items`

Items in a specific version.

- `id` (uuid, pk)
- `version_id` (uuid, fk -> codebook_versions.id)
- `client_id` (uuid, fk -> clients.id) — denormalized for convenience
- `original_label` (text) — raw label from upload
- `description` (text, optional)
- `code` (text) — generated or existing code (e.g. `2-DIP-08-B`)
- `application` (text, optional) — e.g. sanitary, storm, water
- `csi_division` (text, optional)
- `csi_section` (text, optional)
- `metadata` (jsonb, optional) — diameter, material, class, etc.
- `created_at` (timestamptz)

Indexes:
- `(client_id, version_id)`
- `code` (for quick lookup)

---

## 5. `codebook_rules`

Rules/preferences controlling how codes are generated & organized.

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id)
- `codebook_id` (uuid, fk -> codebooks.id, nullable) — null = global for client
- `name` (text)
- `is_active` (boolean)
- `rules_json` (jsonb) — e.g.
  - ordering strategy (material-first, diameter-first, CSI-first)
  - naming templates (e.g. `"${family}-${material}-${diameter}-${type_code}"`)
  - grouping rules (application, division, etc.)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)

---

## 6. `codebook_recommendations`

LLM-generated suggestions tied to a version.

- `id` (uuid, pk)
- `version_id` (uuid, fk -> codebook_versions.id)
- `client_id` (uuid, fk -> clients.id)
- `item_id` (uuid, fk -> codebook_items.id, nullable) — null if global suggestion
- `category` (text) — e.g. `csi_mapping`, `naming`, `grouping`, `missing_item`
- `suggestion` (text)
- `suggestion_payload` (jsonb) — structured change instructions
- `status` (text) — `pending`, `accepted`, `rejected`, etc.
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `acted_by` (text or uuid, optional)

---

## 7. `audit_log`

Records every significant change for traceability.

- `id` (uuid, pk)
- `client_id` (uuid, fk -> clients.id)
- `codebook_id` (uuid, fk -> codebooks.id, nullable)
- `version_id` (uuid, fk -> codebook_versions.id, nullable)
- `action_type` (text) — e.g. `initial_import`, `rule_update`, `version_created`, `recommendation_applied`, `revert`
- `performed_by` (text or uuid, nullable)
- `summary` (text)
- `details` (jsonb) — before/after diffs, rule IDs, etc.
- `created_at` (timestamptz)

Indexes:
- `(client_id, created_at)`
- `(client_id, codebook_id, created_at)`

---

## 8. Vector Metadata (optional tables)

Pinecone will hold the actual vectors, but you may want a local index:

### `item_embeddings`

- `id` (uuid, pk)
- `client_id` (uuid)
- `item_id` (uuid, fk -> codebook_items.id)
- `pinecone_id` (text) — ID used in Pinecone
- `created_at` (timestamptz)

### `csi_embeddings`

- `id` (uuid, pk)
- `client_id` (uuid, nullable) — global if null
- `csi_code` (text)
- `csi_title` (text)
- `pinecone_id` (text)
- `created_at` (timestamptz)

---

This layout is intentionally flexible; the implementing engineer can optimize and normalize
further as needed.
