# API Documentation

This document specifies the REST API endpoints for the Construction Codebook AI Backend.

---

## Base URL

```
Production: https://api.codebook.example.com/v1
Development: http://localhost:8000/v1
```

## Authentication

All requests require authentication via API key in the `Authorization` header:

```http
Authorization: Bearer <API_KEY>
```

Rate limits:
- Standard operations: 100 requests/minute
- LLM-heavy operations (analysis, refactor): 10 requests/hour

---

## Response Format

### Success Response
```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "INVALID_CODEBOOK_TYPE",
    "message": "Codebook type must be material, activity, or bid_item",
    "details": { ... },
    "request_id": "uuid"
  }
}
```

### Paginated Response
```json
{
  "data": [ ... ],
  "pagination": {
    "next_cursor": "base64_encoded_cursor",
    "prev_cursor": "base64_encoded_cursor",
    "has_more": true,
    "total_count": 1523
  },
  "meta": { ... }
}
```

---

## Endpoints

### Clients

#### Create Client
```http
POST /clients
```

**Request Body:**
```json
{
  "name": "ACME Construction",
  "slug": "acme-construction",
  "contact_email": "contact@acme.example.com",
  "metadata": {
    "industry": "civil_construction",
    "region": "pacific_northwest"
  }
}
```

**Response:** `201 Created`
```json
{
  "data": {
    "id": "uuid",
    "name": "ACME Construction",
    "slug": "acme-construction",
    "contact_email": "contact@acme.example.com",
    "metadata": { ... },
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
}
```

#### List Clients
```http
GET /clients?limit=50&cursor=...
```

**Response:** `200 OK` (paginated)

#### Get Client
```http
GET /clients/{clientId}
```

**Response:** `200 OK`

#### Update Client
```http
PATCH /clients/{clientId}
```

**Request Body:** (partial update)
```json
{
  "name": "ACME Construction Co.",
  "metadata": { ... }
}
```

**Response:** `200 OK`

#### Delete Client (Soft Delete)
```http
DELETE /clients/{clientId}
```

**Response:** `204 No Content`

---

### Codebooks

#### Create Codebook
```http
POST /clients/{clientId}/codebooks
```

**Request Body:**
```json
{
  "name": "Main Material Codebook",
  "type": "material",
  "description": "Primary material codebook for ACME projects"
}
```

**Response:** `201 Created`

#### Upload Codebook (First Import)
```http
POST /clients/{clientId}/codebooks/upload
```

**Content-Type:** `multipart/form-data` or `application/json`

**Form Data:**
- `file`: CSV/Excel file (max 10MB, max 10,000 rows)
- `name`: Codebook name
- `type`: material | activity | bid_item
- `description`: Optional description

**JSON Body (alternative):**
```json
{
  "name": "Material Codebook",
  "type": "material",
  "description": "...",
  "items": [
    {
      "original_label": "8\" DIP Bend",
      "description": "Ductile iron pipe bend, 8 inch diameter",
      "metadata": {
        "diameter": "8",
        "material": "DIP",
        "type": "bend"
      }
    }
  ]
}
```

**Response:** `202 Accepted` (async operation)
```json
{
  "data": {
    "job_id": "uuid",
    "status": "pending",
    "message": "Codebook upload is being processed"
  }
}
```

#### List Codebooks
```http
GET /clients/{clientId}/codebooks?type=material&limit=50&cursor=...
```

**Query Parameters:**
- `type`: Filter by type (material | activity | bid_item)
- `limit`: Page size (default 50, max 500)
- `cursor`: Pagination cursor

**Response:** `200 OK` (paginated)

#### Get Codebook
```http
GET /codebooks/{codebookId}
```

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "client_id": "uuid",
    "name": "Material Codebook",
    "type": "material",
    "description": "...",
    "created_at": "...",
    "updated_at": "...",
    "active_version": {
      "id": "uuid",
      "version_number": 3,
      "label": "Post-refactor 1",
      "created_at": "..."
    }
  }
}
```

#### Delete Codebook
```http
DELETE /codebooks/{codebookId}
```

**Response:** `204 No Content`

---

### Versions

#### List Versions
```http
GET /codebooks/{codebookId}/versions?limit=50&cursor=...
```

**Response:** `200 OK` (paginated)

#### Get Version Details
```http
GET /codebook-versions/{versionId}
```

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "codebook_id": "uuid",
    "version_number": 2,
    "label": "Initial import",
    "notes": "...",
    "rules_snapshot": {
      "ordering_strategy": "material-first",
      "naming_template": "${family}-${material}-${diameter}-${type_code}"
    },
    "analysis_summary": "Codebook structure is generally consistent...",
    "analysis_details": { ... },
    "prompt_version": "analysis_v1.0",
    "is_active": true,
    "created_by": "user@example.com",
    "created_at": "...",
    "item_count": 127
  }
}
```

#### Get Version Items
```http
GET /codebook-versions/{versionId}/items?limit=100&cursor=...&csi_division=33
```

**Query Parameters:**
- `limit`: Page size
- `cursor`: Pagination cursor
- `csi_division`: Filter by CSI division
- `application`: Filter by application (sanitary_sewer | storm_sewer | water | other)
- `search`: Full-text search on labels and descriptions

**Response:** `200 OK` (paginated)
```json
{
  "data": [
    {
      "id": "uuid",
      "version_id": "uuid",
      "client_id": "uuid",
      "original_label": "8\" DIP Bend",
      "description": "...",
      "code": "2-DIP-08-B",
      "application": "sanitary_sewer",
      "csi_division": "33",
      "csi_section": "33 30 00",
      "metadata": {
        "diameter": "8",
        "material": "DIP",
        "type": "bend"
      },
      "created_at": "..."
    }
  ],
  "pagination": { ... }
}
```

---

### Rules

#### Create or Update Rules
```http
POST /codebooks/{codebookId}/rules
```

**Request Body:**
```json
{
  "name": "Material-first ordering with CSI grouping",
  "is_active": true,
  "rules_json": {
    "ordering_strategy": "material-first",
    "naming_template": "${family}-${material}-${diameter}-${type_code}",
    "grouping": {
      "primary": "material",
      "secondary": "application",
      "tertiary": "csi_division"
    },
    "code_format": {
      "separator": "-",
      "family_prefix": "2",
      "material_codes": {
        "DIP": "DIP",
        "PVC": "PVC",
        "HDPE": "HDPE"
      }
    }
  }
}
```

**Response:** `201 Created`

#### List Rules
```http
GET /clients/{clientId}/rules?codebook_id={codebookId}&active_only=true
```

**Response:** `200 OK`

---

### Refactor / Analysis

#### Trigger Refactor
```http
POST /codebooks/{codebookId}/refactor
```

**Request Body:**
```json
{
  "rule_id": "uuid",
  "label": "Switched to diameter-first ordering",
  "notes": "Client requested diameter to be the primary grouping factor"
}
```

**Response:** `202 Accepted`
```json
{
  "data": {
    "job_id": "uuid",
    "status": "pending",
    "message": "Refactor job has been queued"
  }
}
```

#### Trigger Re-analysis
```http
POST /codebook-versions/{versionId}/analyze
```

**Request Body:**
```json
{
  "focus_areas": ["csi_mapping", "inconsistencies", "missing_items"]
}
```

**Response:** `202 Accepted`

---

### Recommendations

#### List Recommendations
```http
GET /codebook-versions/{versionId}/recommendations?status=pending&limit=50&cursor=...
```

**Query Parameters:**
- `status`: Filter by status (pending | accepted | rejected | dismissed)
- `category`: Filter by category (csi_mapping | naming | grouping | missing_item | inconsistency | other)
- `limit`: Page size
- `cursor`: Pagination cursor

**Response:** `200 OK` (paginated)
```json
{
  "data": [
    {
      "id": "uuid",
      "version_id": "uuid",
      "client_id": "uuid",
      "item_id": "uuid",
      "category": "csi_mapping",
      "suggestion": "This item should be mapped to CSI Division 33 (Utilities) instead of Division 02",
      "suggestion_payload": {
        "current_csi_division": "02",
        "suggested_csi_division": "33",
        "suggested_csi_section": "33 30 00",
        "confidence": 0.92
      },
      "status": "pending",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "pagination": { ... }
}
```

#### Accept Recommendation
```http
POST /recommendations/{recommendationId}/accept
```

**Request Body:**
```json
{
  "notes": "Client approved this mapping change"
}
```

**Response:** `202 Accepted` (may trigger async job if changes are significant)

#### Reject Recommendation
```http
POST /recommendations/{recommendationId}/reject
```

**Request Body:**
```json
{
  "reason": "Client prefers current CSI division",
  "feedback": "DIP items should remain in Division 02 per client standard"
}
```

**Response:** `200 OK`

#### Batch Action on Recommendations
```http
POST /recommendations/batch-action
```

**Request Body:**
```json
{
  "recommendation_ids": ["uuid1", "uuid2", "uuid3"],
  "action": "accept",
  "notes": "Bulk approval of CSI mapping recommendations"
}
```

**Response:** `202 Accepted`

---

### Revert

#### Revert to Previous Version
```http
POST /codebooks/{codebookId}/revert
```

**Request Body:**
```json
{
  "target_version_number": 2,
  "label": "Reverted to pre-refactor state",
  "reason": "Client requested rollback of recent changes"
}
```

**Response:** `202 Accepted`
```json
{
  "data": {
    "job_id": "uuid",
    "message": "Revert operation queued"
  }
}
```

---

### Semantic Search

#### Search Codebook Items
```http
POST /clients/{clientId}/search
```

**Request Body:**
```json
{
  "query": "Find all DIP bends around 8 inch diameter for sanitary sewer",
  "codebook_id": "uuid",
  "limit": 20,
  "filters": {
    "type": "material",
    "application": "sanitary_sewer"
  }
}
```

**Response:** `200 OK`
```json
{
  "data": {
    "results": [
      {
        "item": {
          "id": "uuid",
          "code": "2-DIP-08-B",
          "original_label": "8\" DIP Bend",
          "description": "...",
          "metadata": { ... }
        },
        "score": 0.94,
        "version_id": "uuid",
        "codebook_name": "Material Codebook"
      }
    ],
    "query": "...",
    "result_count": 5
  }
}
```

---

### Jobs

#### Get Job Status
```http
GET /jobs/{jobId}
```

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "client_id": "uuid",
    "codebook_id": "uuid",
    "job_type": "refactor",
    "status": "running",
    "progress": 67,
    "result": null,
    "error": null,
    "started_at": "...",
    "completed_at": null,
    "created_at": "...",
    "created_by": "user@example.com"
  }
}
```

#### List Jobs
```http
GET /clients/{clientId}/jobs?status=running&limit=50&cursor=...
```

**Response:** `200 OK` (paginated)

#### Cancel Job
```http
POST /jobs/{jobId}/cancel
```

**Response:** `200 OK`

---

### Audit Log

#### Get Audit Log
```http
GET /clients/{clientId}/audit-log?codebook_id=uuid&action_type=refactor_completed&limit=100&cursor=...
```

**Query Parameters:**
- `codebook_id`: Filter by codebook
- `action_type`: Filter by action type
- `from_date`: ISO 8601 timestamp
- `to_date`: ISO 8601 timestamp
- `limit`: Page size
- `cursor`: Pagination cursor

**Response:** `200 OK` (paginated)
```json
{
  "data": [
    {
      "id": "uuid",
      "client_id": "uuid",
      "codebook_id": "uuid",
      "version_id": "uuid",
      "action_type": "refactor_completed",
      "performed_by": "user@example.com",
      "summary": "Refactored codebook to diameter-first ordering",
      "details": {
        "rule_id": "uuid",
        "items_changed": 127,
        "before_snapshot": { ... },
        "after_snapshot": { ... }
      },
      "llm_tokens_used": 15234,
      "created_at": "..."
    }
  ],
  "pagination": { ... }
}
```

---

### Export

#### Export Codebook Version
```http
GET /codebook-versions/{versionId}/export?format=csv
```

**Query Parameters:**
- `format`: csv | excel | json | hcss

**Response:** `200 OK`
- Content-Type: `text/csv` or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` or `application/json`
- Content-Disposition: `attachment; filename="codebook-v3-2025-01-15.csv"`

---

### LLM Usage

#### Get LLM Usage Report
```http
GET /clients/{clientId}/llm-usage?from_date=2025-01-01&to_date=2025-01-31
```

**Query Parameters:**
- `from_date`: ISO 8601 date
- `to_date`: ISO 8601 date
- `group_by`: operation_type | model_name | day | month

**Response:** `200 OK`
```json
{
  "data": {
    "summary": {
      "total_tokens": 1245678,
      "total_cost_usd": 45.23,
      "operations_count": 89
    },
    "breakdown": [
      {
        "operation_type": "refactor",
        "model_name": "gpt-4o",
        "tokens_total": 523456,
        "cost_usd": 25.67,
        "count": 12
      }
    ]
  }
}
```

---

## HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted, processing asynchronously
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid request body or parameters
- `401 Unauthorized` - Missing or invalid API key
- `403 Forbidden` - API key lacks required permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Concurrent modification detected
- `413 Payload Too Large` - File upload exceeds size limit
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - External service (LLM, Pinecone) unavailable

---

## Webhooks (Optional Future Enhancement)

### Register Webhook
```http
POST /clients/{clientId}/webhooks
```

**Request Body:**
```json
{
  "url": "https://example.com/webhooks/codebook-events",
  "events": ["codebook.refactor.completed", "job.completed", "job.failed"],
  "secret": "webhook_signing_secret"
}
```

### Webhook Payload Example
```json
{
  "event": "codebook.refactor.completed",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "job_id": "uuid",
    "codebook_id": "uuid",
    "new_version_id": "uuid",
    "version_number": 4
  }
}
```

---

## SDK Examples

### JavaScript/TypeScript
```typescript
import { CodebookClient } from '@codebook/client';

const client = new CodebookClient({
  apiKey: process.env.CODEBOOK_API_KEY,
  baseUrl: 'https://api.codebook.example.com/v1'
});

// Upload codebook
const job = await client.codebooks.upload(clientId, {
  name: 'Material Codebook',
  type: 'material',
  file: fileBuffer
});

// Poll for completion
const result = await client.jobs.waitForCompletion(job.job_id);
```

### Python
```python
from codebook_client import CodebookClient

client = CodebookClient(
    api_key=os.environ['CODEBOOK_API_KEY'],
    base_url='https://api.codebook.example.com/v1'
)

# Upload codebook
job = client.codebooks.upload(
    client_id=client_id,
    name='Material Codebook',
    type='material',
    file=open('codebook.csv', 'rb')
)

# Poll for completion
result = client.jobs.wait_for_completion(job.job_id)
```

---

## Notes

- All timestamps are in ISO 8601 format with UTC timezone
- UUIDs are returned as strings
- Cursor-based pagination is preferred over offset for performance
- All async operations return a `job_id` for status tracking
- File uploads must use `multipart/form-data` encoding
- Large result sets are automatically paginated
