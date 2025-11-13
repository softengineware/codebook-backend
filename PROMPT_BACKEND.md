# One-Shot Prompt for Backend Generation

You can paste this prompt into your code-focused LLM (e.g., GPT-4, GPT-5 Code, Claude Code)
to generate the initial backend implementation.

---

## Prompt

**Role**  
You are an expert software engineer and architect specializing in AI-powered backend systems
for construction and civil engineering workflows. You write production-grade, modular,
secure, and well-documented code.

**Goal**  
Build a backend service that powers a **multi-client construction codebook assistant**.
The system generates, analyzes, and refines **material**, **activity**, and **bid item**
codebooks. It uses:

- **Supabase (PostgreSQL/SQL)** for structured data
- **Pinecone** for vector search over embeddings
- An **LLM** (this or another model) for intelligence and recommendations

The code you produce should be ready to run after environment variables are configured
and dependencies are installed.

---

## Functional Requirements

1. **Multi-client support**
   - Each client has:
     - One or more codebooks
     - Preferences and rules for how codes should be generated and organized
   - Ensure strong separation of data by `client_id` in all queries.

2. **Codebook types**
   - Support at least three types:
     - `material`
     - `activity`
     - `bid_item`
   - Each type can have its own nuances in how codes are generated and organized.

3. **Upload & initial analysis**
   - Provide an endpoint to upload a codebook for the first time, e.g. as CSV/JSON.
   - On first upload for a given codebook:
     - Parse items (materials, activities, or bid items).
     - Store them in Supabase with a **version 1** record.
     - Call the LLM to:
       - Evaluate the current structure and naming
       - Map items to likely **CSI MasterFormat divisions**
       - Suggest a clearer structure or alternative coding schemes
     - Store:
       - The analysis text
       - Structured recommendations (e.g. JSON)
       - A summary of key findings
     - Generate embeddings for relevant text and store them in **Pinecone** for later retrieval.

4. **Flexible coding & refactoring**
   - The system must support user-defined coding rules such as:
     - Material-based codes, e.g. `2-DIP`, `2-PVC`, etc.
     - Application-based grouping (sanitary sewer, storm sewer, water, etc.).
     - Ordering by diameter first (e.g. `2-DIP-08` then `B` for bends, `T` for tees, etc.).
     - Rough organization by CSI MasterFormat divisions.
   - Provide endpoints to:
     - Define or update a client’s codebook rules/preferences.
     - Request that an existing codebook be **refactored** under new rules
       (e.g. change from material-first to diameter-first ordering).
     - The backend should:
       - Fetch the current version from Supabase
       - Retrieve relevant context from Pinecone (e.g. similar items, CSI info)
       - Call the LLM to propose new codes and ordering
       - Store the proposed refactored codebook as a **new version** (pending user approval)
       - Provide a structured diff/summary of changes.

5. **Recommendations and feedback loop**
   - LLM should not only follow rules, but also **make recommendations**:
     - Suggest missing items, misclassified items, or better CSI mappings.
     - Point out inconsistencies in naming, sizing, or grouping.
   - Provide endpoints to:
     - List recommendations for a codebook version
     - Accept or reject each recommendation
     - Submit free-form user feedback that updates preferences/rules
   - All accepted changes should create a **new version** and write entries into an **audit log**.

6. **Versioning & audit log**
   - Every codebook has:
     - A monotonically increasing `version_number`
     - A snapshot of items per version
   - Maintain an **audit log** with:
     - Who/what triggered a change (user or system)
     - What was changed (summary + structured payload)
     - Timestamps and associated `client_id`, `codebook_id`, and `version_id`
   - Provide endpoints to:
     - List versions
     - View details of a specific version
     - View the audit log (with filtering by client, codebook, and date)
     - Revert to a previous version:
       - Create a **new version** whose content matches the selected past version
       - Log the revert action in the audit log.

7. **Pinecone integration**
   - Use Pinecone to store embeddings for:
     - Codebook items (names, descriptions)
     - CSI division descriptions and examples
     - LLM analyses and recommendations (where useful)
   - Expose an endpoint for:
     - Semantic search over a client’s codebook items (e.g. “find all DIP bends around 8-inch diameter”)
   - Design a clear **index/namespace strategy** to separate data per client.

8. **Security & multi-tenancy**
   - All requests must be scoped to a `client_id` (or equivalent tenant identifier).
   - Do not leak data between clients.
   - Validate inputs and avoid SQL injection or unsafe queries.

---

## Technical Requirements & Best Practices

- Use a clean, modular architecture (e.g. controllers/routes, services, repositories, utils).
- Encapsulate Supabase access in a dedicated module or service.
- Encapsulate Pinecone access in a dedicated module or service.
- Encapsulate LLM calls in a dedicated `llmClient` or similar abstraction.
- Use configuration and environment variables for:
  - Supabase URL and service key
  - Pinecone API key, environment/index names
  - LLM API key and model names
- Implement basic error handling and logging.
- Provide docstrings/comments on key functions and data models.
- Prefer clear, maintainable code over cleverness.

---

## Data Model (High-Level)

Use this as guidance; you may refine as needed. See `DATA_MODEL.md` in the repo for more detail.

- `clients`
- `codebooks`
- `codebook_versions`
- `codebook_items`
- `codebook_rules` (per client and/or per codebook)
- `codebook_recommendations`
- `audit_log`

Ensure foreign keys and indices are appropriate for querying by `client_id`, `codebook_id`, and `version_id`.

---

## Output Expectations

- Create all necessary backend code files and basic project structure.
- Include:
  - Database access layer
  - Pinecone client
  - LLM client
  - REST API routes/handlers for the functionality described
- Include any helper scripts (e.g. for initializing schema/migrations) as appropriate.
- Provide minimal inline documentation explaining how to run and configure the service.

When you respond, output **only code and configuration files**, not natural-language explanations.
Group code by file, clearly marking file paths.
