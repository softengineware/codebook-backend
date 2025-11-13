# Implementation Tasks

Use this as a checklist / roadmap for building the backend.

---

## Phase 0 – Project Setup

- [ ] Choose backend stack (e.g. Node/TypeScript, Python/FastAPI).
- [ ] Initialize project (package manager, basic folder structure).
- [ ] Add configuration loader (env variables).
- [ ] Add logger and basic error-handling middleware.
- [ ] Initialize Git repo and commit scaffold.

---

## Phase 1 – Supabase / Database

- [ ] Create Supabase project.
- [ ] Apply SQL schema from `DATA_MODEL.md` (or adapted version).
- [ ] Implement DB client module (Supabase SDK or Postgres driver).
- [ ] Implement repository layer for:
  - [ ] Clients
  - [ ] Codebooks
  - [ ] Codebook versions
  - [ ] Codebook items
  - [ ] Rules
  - [ ] Recommendations
  - [ ] Audit log

---

## Phase 2 – Pinecone Integration

- [ ] Create Pinecone index and decide on vector dimensions/model.
- [ ] Implement Pinecone client wrapper (init, upsert, query, delete).
- [ ] Implement helpers for:
  - [ ] Creating embeddings (using LLM or embedding model).
  - [ ] Upserting item embeddings.
  - [ ] Querying items by similarity.
  - [ ] Managing namespaces / client separation.

---

## Phase 3 – LLM Integration

- [ ] Implement LLM client (prompt + completion abstraction).
- [ ] Implement prompt templates for:
  - [ ] Initial codebook analysis.
  - [ ] Refactor under new rules.
  - [ ] Recommendation summarization & explanation.
- [ ] Implement mappers to convert LLM responses into:
  - [ ] Analyses (stored on versions).
  - [ ] Recommendations (rows in `codebook_recommendations`).
  - [ ] Updated codes and items.

---

## Phase 4 – Core API Endpoints

- [ ] `POST /clients` – create client.
- [ ] `GET /clients` – list clients.
- [ ] `POST /clients/{clientId}/codebooks` – create codebook + first upload.
- [ ] `GET /clients/{clientId}/codebooks` – list codebooks.
- [ ] `GET /codebooks/{id}` – codebook details + active version.
- [ ] `GET /codebooks/{id}/versions` – list versions.
- [ ] `GET /codebook-versions/{versionId}` – version details + items.
- [ ] `POST /codebooks/{id}/rules` – create/update rules.
- [ ] `POST /codebooks/{id}/refactor` – trigger refactor under rules.
- [ ] `GET /codebook-versions/{versionId}/recommendations` – list recommendations.
- [ ] `POST /recommendations/{id}/accept` – apply recommendation.
- [ ] `POST /recommendations/{id}/reject` – reject recommendation.
- [ ] `POST /codebooks/{id}/revert` – revert to previous version.
- [ ] `GET /clients/{clientId}/audit-log` – view audit entries.
- [ ] `GET /clients/{clientId}/search` – semantic search via Pinecone.

---

## Phase 5 – Testing & Hardening

- [ ] Unit tests for service layer (rules, versioning, audit logging).
- [ ] Integration tests for API endpoints.
- [ ] Load tests (basic) for large codebooks.
- [ ] Review error handling and logging.
- [ ] Verify no data leaks between clients.

---

## Phase 6 – Deployment

- [ ] Choose deployment target (e.g. Render, Fly.io, Railway, etc.).
- [ ] Set environment variables in deployment platform.
- [ ] Document deploy steps in `README.md`.
- [ ] Set up basic monitoring/alerts (if available).
