# Construction Codebook AI Backend

## Overview

This project defines the backend for an AI-assisted system that helps a civil construction consultant
generate, analyze, and maintain **material**, **activity**, and **bid item** codebooks for multiple clients.

The system uses:

- **Supabase (PostgreSQL/SQL)** for structured data: clients, codebooks, versions, audit logs, preferences.
- **Pinecone (vector database)** for semantic search and retrieval over embeddings of:
  - Codebook items
  - CSI MasterFormat divisions and descriptions
  - LLM-generated analyses and recommendations
- An **LLM (large language model)** for:
  - Understanding uploaded codebooks
  - Mapping items into CSI-style structures
  - Generating and refactoring codes
  - Making recommendations and explaining changes

The goal is to support an iterative consulting workflow where each client’s codebooks can be refined
over time, with full version history and a solid audit trail of every recommendation and change.

---

## Key Features

- **Multi-codebook support**
  - Material codebooks
  - Activity codebooks
  - Bid item codebooks

- **Flexible coding rules**
  - Codes can be generated or refactored based on user-defined rules, e.g.:
    - Start with material family (e.g. `2-DIP`, `2-PVC`)
    - Sort/group by application (sanitary sewer, storm sewer, water, etc.)
    - Sort/group using CSI MasterFormat divisions
    - Change ordering strategies (e.g. material → diameter vs. diameter → type)

- **CSI MasterFormat awareness**
  - LLM understands CSI-style divisions and can:
    - Suggest likely CSI divisions and subcategories for items
    - Recommend codebook structures that “make sense” in that framework
    - Highlight inconsistencies, gaps, or misclassifications

- **First-upload analysis**
  - When a codebook is uploaded for the first time:
    - LLM evaluates the structure, naming, and organization
    - Generates an **analysis report** and **recommendations**
    - Stores the report, recommendations, and associated embeddings

- **Iterative refinement workflow**
  - User can:
    - Accept or reject recommendations
    - Provide feedback that updates the rules
    - Ask for alternate organizations (e.g. re-order by diameter first)
  - LLM applies new rules to regenerate codes and mappings.

- **Versioning and audit log**
  - Every material/activity/bid item codebook has:
    - A **version history**
    - A **detailed audit log** of changes and decisions
  - Ability to **revert** to any previous version.

- **Multi-client support**
  - Each client has:
    - Their own codebooks
    - Their own rules/preferences
    - Separate histories and audit logs
  - Data is clearly partitioned per client.

---

## High-Level Architecture

- **Backend service**
  - Exposes APIs for:
    - Managing clients and codebooks
    - Uploading items (CSV/Excel/text)
    - Requesting analyses and recommendations from the LLM
    - Viewing versions and audit logs
    - Applying/refining rules and regenerating codes

- **Supabase (SQL)**
  - Stores:
    - Clients and users
    - Codebooks and their metadata
    - Codebook versions and items per version
    - Rule configurations and client preferences
    - Analyses, recommendation snapshots
    - Audit log records

- **Pinecone (Vector)**
  - Stores embeddings for:
    - Codebook items
    - CSI division descriptions and examples
    - Past analyses and decisions (for context)
  - Enables semantic search and similarity-based recommendations.

- **LLM integration**
  - Given:
    - Codebook items (and/or current structure)
    - Client preferences and rules
    - Relevant CSI context (retrieved from Pinecone)
  - LLM returns:
    - Suggested codes and hierarchy
    - Explanations and analyses
    - Suggested changes and refinements

The concrete language & framework for the backend (e.g. Node/TypeScript, Python/FastAPI, etc.)
can be chosen by the implementing engineer or generated using the provided one-shot prompt.

---

## Project Files in This Scaffold

- `README.md` — This overview.
- `PROMPT_BACKEND.md` — One-shot prompt for the LLM to generate the backend implementation.
- `SPEC.md` — Product & technical specification.
- `DATA_MODEL.md` — Suggested Supabase (SQL) schema design.
- `ARCHITECTURE.md` — System architecture and integration details.
- `TASKS.md` — Implementation task list / roadmap.
- `.env.example` — Example environment variables.
- `.gitignore` — Standard ignore rules for a mixed JS/Python backend.

---

## Getting Started (for a developer)

1. **Choose backend stack**
   - Recommended: a framework with good HTTP + database + async support (e.g. Node/TypeScript, Python/FastAPI).
2. **Create infrastructure**
   - Spin up a Supabase project (PostgreSQL).
   - Spin up a Pinecone index (for semantic search).
   - Obtain LLM API credentials (e.g. OpenAI, Anthropic, etc.).
3. **Review the docs in this repo**
   - `SPEC.md` for requirements
   - `DATA_MODEL.md` for schema
   - `ARCHITECTURE.md` for integration
   - `PROMPT_BACKEND.md` to generate initial implementation with an LLM
4. **Implement MVP**
   - Use `TASKS.md` as a checklist.
   - Generate starter code with the one-shot prompt and then refine as needed.
5. **Iterate with real client data**
   - Start with an internal or pilot client.
   - Upload sample codebooks.
   - Measure and refine the quality of analyses and recommendations.
