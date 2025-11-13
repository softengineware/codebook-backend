# Specification – Construction Codebook AI Backend

## 1. Background & Goals

A civil construction consultant manages **material**, **activity**, and **bid item** codebooks
for multiple clients. Each client has different preferences for how items are coded and organized,
and these preferences evolve over time.

Current pain points:
- Manually structuring and restructuring codebooks is slow and error-prone.
- Keeping a clear version history and audit trail is difficult.
- Mapping items into CSI MasterFormat-style structures is non-trivial.
- Different clients want different patterns and conventions.

This backend will:
- Use an LLM to analyze and reorganize codebooks.
- Use Supabase for persistent relational data and versioning.
- Use Pinecone for semantic search/retrieval over codebook & CSI content.
- Provide a clean API to power a future web UI or other integrations.

---

## 2. User Roles

1. **Consultant (owner/admin)**
   - Manages multiple client accounts.
   - Can see and operate on any client’s codebooks.

2. **Client user (optional future extension)**
   - Scoped to one client.
   - Can upload, review, and approve changes for that client’s codebooks.

Initially, the system may only need a consultant-level account; extend later as needed.

---

## 3. Core Use Cases

### 3.1 Onboard new client
- Consultant creates a client record with name, contact, optional metadata.
- System initializes default preferences/rules for that client (can be generic).

### 3.2 Upload first codebook
- Consultant selects client and codebook type (`material`, `activity`, `bid_item`).
- Uploads a list of items (CSV, JSON, etc.).
- Backend:
  - Stores raw upload and parsed items as **version 1**.
  - Calls LLM for:
    - Structure evaluation
    - CSI mapping suggestions
    - Coding/organization suggestions
  - Stores analysis & recommendations.
  - Logs an initial audit entry.

### 3.3 View analysis & recommendations
- Consultant fetches:
  - High-level analysis summary.
  - Detailed recommendations list (e.g. per item or group).
- They can inspect and decide what to apply.

### 3.4 Apply coding rules or refinements
- Consultant defines or refines rules, e.g.:
  - “Material-first codes with leading digit for family (e.g. `2-DIP`, `2-PVC`)”
  - “Within each material, group by application (sanitary, storm, water).”
  - “Reorder to diameter-first, e.g. `2-DIP-08-B` for 8" DIP bend.”
  - “Organize roughly by CSI divisions.”
- Backend:
  - Stores these rules/preferences.
  - Uses LLM + Pinecone to:
    - Propose updated codes and structure.
    - Generate a new version with proposed changes.
  - Logs all changes and recommendations applied or left pending.

### 3.5 Iterate and fine-tune
- Consultant can:
  - Accept or reject recommendations.
  - Provide feedback: “Group tees differently”, “Prefer shorter codes”, etc.
- System uses feedback to refine rules and future LLM prompts.

### 3.6 Add or update items
- Consultant uploads delta lists (new or changed items).
- Backend:
  - Detects new vs. existing items.
  - Generates codes per current rules.
  - Creates a new version capturing the changes.
  - Logs actions.

### 3.7 View history and revert
- Consultant views version history for a codebook.
- Can inspect an older version and its audit trail.
- Can “revert” to a prior version:
  - System creates a new version copying the selected version’s content.
  - Audit log records the revert event.

### 3.8 Semantic search (optional, but strongly desired)
- Consultant queries in natural language:
  - “Show me all DIP bends 8 inch or similar”
  - “Find items related to storm sewer manholes”
- Backend uses Pinecone and LLM to return relevant items.

---

## 4. Functional Requirements (Summary)

- Multi-client tenant structure.
- CRUD for clients and codebooks.
- Upload & parse codebook items.
- First-upload analysis via LLM.
- Rule management (per client and/or per codebook).
- Versioning of codebooks and items.
- Audit log for all operations that change data.
- Integration with Pinecone for semantic search.
- Integration with LLM for:
  - Analyses
  - Code generation/refactoring
  - CSI-based recommendations.
- Ability to revert to previous versions.

---

## 5. Non-Functional Requirements

- **Security & isolation**
  - No data leakage between clients.
  - All queries filtered by `client_id`.
- **Reliability**
  - Avoid partial writes where possible.
  - Use transactions for multi-step updates.
- **Traceability**
  - Every change creates an audit record.
- **Extensibility**
  - Easy to add new codebook types or rule dimensions.
- **Performance**
  - Efficient listing and searching of items.
  - Use indexing and reasonable pagination.

---

## 6. Out of Scope for MVP

- Full-featured user authentication / SSO (can start with simple API keys).
- Complex UI; this spec focuses on backend.
- Real-time collaboration features.
- Billing and subscription management.
