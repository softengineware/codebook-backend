# Implementation Tasks

Use this as a checklist / roadmap for building the backend.

---

## Current Implementation Status (snapshot)

- **Core app & config**: FastAPI app entrypoint in `main.py` with CORS, structured logging, and global error handlers; configuration via `src/core/config.py`.
- **Errors & logging**: Centralized error types in `src/core/errors.py` and JSON/console logging in `src/core/logging_config.py`.
- **Database client**: Supabase client helper implemented in `src/services/database.py` (no repository layer yet).
- **Auth & security**: API-key based auth dependency in `src/api/dependencies/auth.py` wired to Supabase `api_keys` table.
- **Domain models**: Pydantic models for clients, codebooks, and jobs in `src/models/`.
- **API routing**: Routers for health/auth/clients/codebooks/versions/jobs are registered in `main.py`, but route modules under `src/api/routes/` have not been created yet.
- **Integrations**: Pinecone, LLM client, workers, and semantic search are not yet implemented (only error types/config fields exist).
- **Frontend**: Frontend dashboard is planned in Phase 7; `frontend/` project has not been created yet.

---

## Phase 0 – Project Setup

- [x] Choose backend stack (e.g. Node/TypeScript, Python/FastAPI).
- [x] Initialize project (package manager, basic folder structure).
- [x] Add configuration loader (env variables).
- [x] Add logger and basic error-handling middleware.
- [x] Initialize Git repo and commit scaffold.

---

## Phase 1 – Supabase / Database

- [ ] Create Supabase project.
- [ ] Apply SQL schema from `DATA_MODEL.md` (or adapted version).
- [x] Implement DB client module (Supabase SDK or Postgres driver).  _(Implemented in `src/services/database.py`, uses `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`.)_
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

_Note: API surface is fully designed and documented in `API.md`, but endpoints are not yet implemented in `src/api/routes/`._

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

---

## Phase 7 – Frontend Dashboard & Preview

- [ ] Create React + TypeScript frontend using Vite in `frontend/`.
  - Template: `react-ts`.
  - UI stack: Material-UI (MUI), React Router, React Query, Axios.
- [ ] Implement core layout and pages:
  - [ ] Dashboard listing clients/codebooks.
  - [ ] Codebook detail page with items and versions.
  - [ ] Not Found (404) page.
- [ ] Implement components:
  - [ ] Codebook items table with search/pagination.
  - [ ] Version history list with compare/restore actions (wired to backend when ready).
  - [ ] Loading and error states.
- [ ] API integration (real data – no mocks in main flow):
  - [ ] Configure `VITE_API_BASE_URL` (e.g. `http://localhost:8000/api`).
  - [ ] Call the REST endpoints defined in `API.md` for clients, codebooks, versions, and items.
- [ ] Local preview steps (for future sessions):
  - [ ] Backend: run FastAPI app on `http://localhost:8000`.
  - [ ] Frontend: from `frontend/`, run `npm install` then `npm run dev`.
  - [ ] Open the Vite URL in a browser (typically `http://localhost:5173`).
