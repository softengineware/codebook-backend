# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **backend specification repository** for an AI-assisted construction codebook management system. The codebase currently contains planning documents and specifications - **no implementation code exists yet**.

The system helps civil construction consultants generate, analyze, and maintain **material**, **activity**, and **bid item** codebooks for multiple clients using:
- **Supabase (PostgreSQL)** for structured data storage
- **Pinecone** for semantic vector search
- **LLM** for analysis, code generation, and recommendations

## Repository Structure

This is a **documentation-driven project**. All files are specifications:

- `README.md` - Project overview and feature summary
- `SPEC.md` - Detailed product & technical specification with use cases
- `ARCHITECTURE.md` - System architecture and integration patterns
- `DATA_MODEL.md` - Complete Supabase SQL schema design
- `PROMPT_BACKEND.md` - One-shot prompt to generate initial implementation via LLM
- `TASKS.md` - Phase-by-phase implementation checklist
- `.env.example` - Required environment variables

## Key Architecture Concepts

### Multi-Tenant Design
- All data strictly scoped by `client_id`
- Each client has independent codebooks, rules, and preferences
- **Critical**: Never leak data between clients in queries

### Three-Database Strategy
1. **Supabase (SQL)** - Persistent storage for:
   - Clients and codebooks
   - Versioned codebook items
   - Rules/preferences (JSON-based)
   - Audit logs with full change history

2. **Pinecone (Vector)** - Semantic search for:
   - Codebook item embeddings
   - CSI MasterFormat division descriptions
   - Past analyses and recommendations
   - Uses namespaces or ID-prefixes for client separation

3. **LLM** - Intelligence layer for:
   - Initial codebook analysis and CSI mapping
   - Code generation/refactoring based on rules
   - Recommendations and consistency checks

### Versioning System
- Every codebook change creates a new immutable version
- Versions are monotonically numbered per codebook
- Each version stores:
  - Complete snapshot of items with codes
  - Rules snapshot used to generate that version
  - LLM analysis summary and structured recommendations
- Revert creates a **new version** (not a rollback) with previous content

### Flexible Coding Rules
The system supports dynamic code generation rules like:
- Material-first ordering (`2-DIP-08-B` for 8" DIP bend)
- Diameter-first ordering (reorganize existing codes)
- CSI MasterFormat-based grouping
- Application-based sorting (sanitary/storm/water)

Rules are stored as JSON in `codebook_rules.rules_json` and applied via LLM.

## Data Model Key Tables

See `DATA_MODEL.md` for complete schema. Critical tables:

- `clients` - Tenant-level partitioning
- `codebooks` - Groups versions by client and type (material/activity/bid_item)
  - Has `active_version_id` pointing to current version
- `codebook_versions` - Immutable snapshots with:
  - `version_number` - Sequential per codebook
  - `rules_snapshot` - JSON of rules used
  - `analysis_summary` and `analysis_details` - LLM output
- `codebook_items` - Items per version with:
  - `code` - Generated code (e.g., `2-DIP-08-B`)
  - `csi_division` and `csi_section` - MasterFormat mapping
  - `metadata` - JSONB for flexible attributes
- `codebook_rules` - Active rules per client/codebook
- `codebook_recommendations` - LLM suggestions with accept/reject workflow
- `audit_log` - Full change history with before/after diffs

## Implementation Approach

**To generate initial implementation:**
1. Review `SPEC.md` for functional requirements
2. Review `DATA_MODEL.md` for schema
3. Use the prompt in `PROMPT_BACKEND.md` with an LLM to scaffold the backend
4. Follow `TASKS.md` phases for implementation order

**Technology stack is NOT decided** - implementer chooses:
- Suggested: Node/TypeScript or Python/FastAPI
- Must support: HTTP APIs, async operations, database connections

## Environment Configuration

Required variables (from `.env.example`):
```
SUPABASE_URL
SUPABASE_SERVICE_KEY
PINECONE_API_KEY
PINECONE_INDEX_NAME
PINECONE_ENVIRONMENT
LLM_API_KEY
LLM_MODEL_NAME
EMBEDDING_MODEL_NAME
APP_ENV
PORT
```

## Critical Workflows

### First Upload Flow
1. Parse uploaded items (CSV/JSON)
2. Create codebook + version 1 in Supabase
3. Generate embeddings → upsert to Pinecone
4. Call LLM with items + CSI context for analysis
5. Store analysis + recommendations
6. Log to audit_log

### Refactor Flow
1. Fetch current version + active rules
2. Retrieve similar items from Pinecone for context
3. Call LLM with new rules + current codes
4. LLM returns new codes + change summary
5. Create new version with refactored items
6. Log refactor action

### Recommendation Workflow
1. LLM generates recommendations during analysis/refactor
2. Store as rows in `codebook_recommendations` with status='pending'
3. User accepts/rejects via API
4. Accepted recommendations create new version
5. All actions logged to audit_log

## Security Considerations

- **Never skip client_id filtering** in database queries
- Validate all file uploads (size limits, format validation)
- Use prepared statements/parameterized queries (avoid SQL injection)
- Sanitize LLM inputs/outputs
- Consider rate limiting for LLM calls (cost management)

## CSI MasterFormat Integration

CSI MasterFormat is a construction industry standard for organizing specifications:
- Divisions 00-49 (e.g., Division 33 = Utilities)
- Used to classify materials and activities
- LLM must understand CSI divisions to:
  - Map items to appropriate divisions
  - Suggest logical groupings
  - Identify misclassifications

Consider pre-loading CSI division descriptions into Pinecone as reference embeddings.

## Development Notes

- This repo has **no package.json, requirements.txt, or source code yet**
- No build/test/lint commands exist
- Implementation stack is TBD by the developer
- Git repo is not initialized (per environment info)
