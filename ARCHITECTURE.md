# Architecture – Construction Codebook AI Backend

## 1. Overview

The system is a backend API that coordinates three main components:

1. **Supabase (PostgreSQL)**
   - Persistent relational storage for clients, codebooks, versions, items, rules, and audit logs.
2. **Pinecone (Vector DB)**
   - Semantic search and retrieval over embeddings for items, CSI info, and analyses.
3. **LLM service**
   - Interprets codebooks and preferences, proposes codes and structures, and generates analyses.

The backend is stateless; client-specific context is stored in Supabase and Pinecone.

---

## 2. Logical Components

1. **API Layer (HTTP/REST)**
   - Exposes endpoints for:
     - Client & codebook management
     - Upload/parse items
     - Triggering analyses and refactors
     - Listing/accepting/rejecting recommendations
     - Managing rules
     - Version browsing and revert actions
     - Semantic search

2. **Service Layer**
   - Implements business logic:
     - Multi-client scoping
     - Rules evaluation and manipulation
     - Version creation and comparison
     - Audit logging
     - Orchestration of LLM + Pinecone + Supabase interactions

3. **Integration Clients**
   - **Supabase client** for SQL queries (via official SDK or Postgres driver).
   - **Pinecone client** for vector index operations.
   - **LLM client** for prompt construction and responses.

4. **Utilities**
   - CSV/Excel parsers
   - ID and timestamp helpers
   - Configuration loader for environment variables
   - Logging and error handling helpers

---

## 3. Request Flow Examples

### 3.1 First codebook upload

1. Client sends `POST /clients/{clientId}/codebooks` with metadata and file/JSON.
2. API validates and parses input.
3. Service:
   - Creates `codebooks` row.
   - Creates `codebook_versions` row (version 1).
   - Inserts `codebook_items` rows for each parsed item.
   - Generates embeddings for each item and upserts them into Pinecone.
   - Constructs an LLM prompt:
     - Codebook items
     - Any known preferences/rules
     - CSI context (pulled from Pinecone or a static reference dataset)
   - Receives analysis & recommendations from LLM.
   - Stores summary & details in `codebook_versions` and `codebook_recommendations`.
   - Writes an `audit_log` entry (`initial_import`).
4. API responds with version metadata + a key summary of the analysis.

### 3.2 Apply new coding rules / refactor

1. Client sends `POST /codebooks/{id}/rules` to define or update rules.
2. Service stores rules in `codebook_rules` and marks them active.
3. Client triggers `POST /codebooks/{id}/refactor`.
4. Service:
   - Fetches latest active version and rules.
   - Retrieves relevant embeddings from Pinecone (e.g. similar items, CSI hints).
   - Calls LLM with:
     - Current items and codes
     - Desired rule changes (e.g. diameter-first ordering)
   - LLM returns:
     - New codes & grouping
     - A summary of changes
   - Service creates a new `codebook_versions` row.
   - Writes updated `codebook_items` for that version.
   - Logs the refactor in `audit_log`.
5. API responds with the new version and a diff summary.

### 3.3 Revert to previous version

1. Client requests `POST /codebooks/{id}/revert` with `targetVersionNumber`.
2. Service:
   - Loads the target version and its items.
   - Creates a new version whose items copy the target version.
   - Updates `codebooks.active_version_id` to the new version.
   - Logs the revert in `audit_log`.
3. API returns the new version metadata.

---

## 4. Pinecone Strategy

- **Indexing**
  - One index per environment (e.g. `codebooks-dev`, `codebooks-prod`).
  - Use **namespaces** or ID-prefixes to separate data by client.
- **Documents to embed**
  - Codebook item labels and descriptions.
  - CSI MasterFormat descriptions.
  - Optional: summary snippets from past analyses.
- **Metadata**
  - Store `client_id`, `codebook_id`, `version_id`, `item_id`, `csi_code`, etc.
  - Enables filtered search per client or per codebook.

---

## 5. LLM Usage Patterns

- **Initial analysis prompt**
  - Explain the type of codebook (material/activity/bid item).
  - Provide a sample or full list of items.
  - Ask for:
    - CSI mapping
    - Structural evaluation
    - Recommendations for clearer, more consistent codes.

- **Refactor prompt**
  - Provide current codes + structured rules.
  - Clearly describe new target rules: e.g. diameter-first, different grouping.
  - Ask for:
    - New codes
    - Mappings from old to new
    - Any warnings about ambiguity or conflicts.

- **Recommendation refinement**
  - Provide user feedback (e.g. “prefer shorter codes”, “group sewer vs. storm more distinctly”).
  - Ask the LLM to adjust rules JSON or suggest new rule shapes.

The backend should implement reusable prompt templates and keep them configurable.

---

## 6. Configuration

Example environment variables (see `.env.example`):

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`
- `PINECONE_ENVIRONMENT` (if applicable)
- `LLM_API_KEY`
- `LLM_MODEL_NAME`
- `APP_ENV` (e.g. `development`, `production`)

Configuration is loaded once at startup and passed to integration clients.

---

## 7. Future Extensions

- Role-based access control (consultant vs. client users).
- Per-client Pinecone namespaces or per-codebook indexes.
- UI dashboard for visualizing structure, CSI mapping, and version diffs.
- Export formats for HCSS or other estimating systems.
