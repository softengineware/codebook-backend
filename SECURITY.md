# Security Specification

This document defines security, authentication, and authorization requirements for the Construction Codebook AI Backend.

---

## 1. Authentication

### 1.1 API Key Authentication (MVP)

For initial implementation, use API key-based authentication:

**Format:**
```http
Authorization: Bearer <API_KEY>
```

**Requirements:**
- API keys must be UUIDs or cryptographically random strings (minimum 32 bytes)
- Keys are generated server-side and provided to users securely
- Keys must be hashed (using bcrypt or Argon2) before storage
- Support key prefixes for identification (e.g., `ck_live_...`, `ck_test_...`)

**Storage:**
Create an `api_keys` table:
```sql
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key_hash TEXT NOT NULL, -- bcrypt/Argon2 hash
  key_prefix TEXT NOT NULL, -- first 8 chars for identification
  name TEXT NOT NULL, -- e.g. "Production API Key"
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  user_id TEXT, -- optional user identifier
  scopes TEXT[] DEFAULT ARRAY['read', 'write'], -- permission scopes
  last_used_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ, -- optional expiration
  created_at TIMESTAMPTZ DEFAULT NOW(),
  revoked_at TIMESTAMPTZ, -- for key revocation
  CONSTRAINT check_not_expired CHECK (expires_at IS NULL OR expires_at > created_at)
);

CREATE INDEX idx_api_keys_client_id ON api_keys(client_id);
CREATE INDEX idx_api_keys_key_prefix ON api_keys(key_prefix);
CREATE INDEX idx_api_keys_revoked ON api_keys(revoked_at) WHERE revoked_at IS NULL;
```

**Key Rotation:**
- Support generating new keys while keeping old ones valid (with deprecation warnings)
- Automatically revoke keys after expiration date
- Log all key usage with timestamps

**Rate Limiting per API Key:**
- 100 requests/minute for standard operations
- 10 requests/hour for LLM-heavy operations (refactor, analysis)
- Return `429 Too Many Requests` with `Retry-After` header

---

### 1.2 JWT Authentication (Future Enhancement)

For user-facing applications, implement JWT-based authentication:

**Token Structure:**
```json
{
  "sub": "user_id",
  "client_id": "uuid",
  "role": "consultant",
  "scopes": ["read", "write", "admin"],
  "iat": 1234567890,
  "exp": 1234571490
}
```

**Requirements:**
- Use RS256 (RSA signature) for signing
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (30 days)
- Store refresh tokens in database with revocation support
- Implement token rotation on refresh

---

### 1.3 Service Account Authentication

For internal services and background jobs:

**Approach:**
- Use service account API keys with restricted scopes
- Scope examples: `jobs:execute`, `embeddings:generate`, `llm:call`
- Service keys should NOT have `client:delete` or `admin:*` scopes

---

## 2. Authorization

### 2.1 Role-Based Access Control (RBAC)

Define three roles:

#### **Admin/Consultant**
- Full access to all clients
- Can create/delete clients
- Can view all audit logs
- Can manage API keys
- Can configure system settings

#### **Client User**
- Scoped to single client (`client_id` in token/API key)
- Can CRUD codebooks for their client
- Can view/accept/reject recommendations for their client
- Cannot delete client or manage API keys
- Cannot access other clients' data

#### **Read-Only User**
- Scoped to single client
- Can view codebooks, versions, items, recommendations
- Cannot create, update, or delete anything
- Cannot accept/reject recommendations

**Implementation:**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'client_user', 'readonly')),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE, -- null for admin
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_client_id ON users(client_id);
```

---

### 2.2 Permission Matrix

| Resource            | Admin | Client User | Read-Only |
|---------------------|-------|-------------|-----------|
| List all clients    | ✅     | ❌           | ❌         |
| View own client     | ✅     | ✅           | ✅         |
| Create client       | ✅     | ❌           | ❌         |
| Delete client       | ✅     | ❌           | ❌         |
| Create codebook     | ✅     | ✅           | ❌         |
| Upload items        | ✅     | ✅           | ❌         |
| View codebook       | ✅     | ✅           | ✅         |
| Refactor codebook   | ✅     | ✅           | ❌         |
| Delete codebook     | ✅     | ✅           | ❌         |
| View recommendations| ✅     | ✅           | ✅         |
| Accept/reject recs  | ✅     | ✅           | ❌         |
| View audit log      | ✅     | ✅ (own)     | ✅ (own)   |
| Manage API keys     | ✅     | ❌           | ❌         |
| View LLM usage      | ✅     | ✅ (own)     | ✅ (own)   |

---

### 2.3 Data Scoping

**Critical Security Rule:** All database queries MUST be scoped by `client_id` unless user is admin.

**Implementation Pattern:**

```typescript
// BAD - Unscoped query (security vulnerability!)
const codebooks = await db.query('SELECT * FROM codebooks WHERE id = $1', [codebookId]);

// GOOD - Scoped query
const codebooks = await db.query(
  'SELECT * FROM codebooks WHERE id = $1 AND client_id = $2',
  [codebookId, userClientId]
);
```

**Middleware Example:**
```typescript
function requireClientAccess(req, res, next) {
  const { client_id } = req.params;
  const userClientId = req.auth.client_id;
  const isAdmin = req.auth.role === 'admin';

  if (!isAdmin && client_id !== userClientId) {
    return res.status(403).json({
      error: {
        code: 'FORBIDDEN',
        message: 'You do not have access to this client'
      }
    });
  }

  next();
}
```

---

## 3. Input Validation & Sanitization

### 3.1 Request Validation

**Requirements:**
- Validate all input against schemas (use JSON Schema, Zod, Joi, or Pydantic)
- Reject requests with unexpected fields (strict parsing)
- Enforce type constraints (strings, numbers, UUIDs, enums)
- Validate string lengths (max 255 for names, max 10MB for files)

**Example Validation Schema (JSON Schema):**
```json
{
  "type": "object",
  "required": ["name", "type"],
  "additionalProperties": false,
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255
    },
    "type": {
      "type": "string",
      "enum": ["material", "activity", "bid_item"]
    },
    "description": {
      "type": "string",
      "maxLength": 2000
    }
  }
}
```

---

### 3.2 SQL Injection Prevention

**Requirements:**
- ALWAYS use parameterized queries or ORM query builders
- NEVER concatenate user input into SQL strings
- Use Supabase client's built-in escaping
- Validate UUIDs before use

**Examples:**

```typescript
// BAD - SQL injection vulnerability!
const items = await db.query(`SELECT * FROM codebook_items WHERE code = '${userInput}'`);

// GOOD - Parameterized query
const items = await db.query('SELECT * FROM codebook_items WHERE code = $1', [userInput]);

// GOOD - ORM query builder
const items = await supabase
  .from('codebook_items')
  .select('*')
  .eq('code', userInput);
```

---

### 3.3 File Upload Security

**CSV/Excel Upload Requirements:**
- Max file size: 10MB
- Max rows: 10,000
- Allowed MIME types:
  - `text/csv`
  - `application/vnd.ms-excel`
  - `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Scan for malicious content (consider ClamAV or similar)
- Parse in streaming mode to prevent memory exhaustion
- Validate CSV headers and column count
- Sanitize cell values (remove null bytes, control characters)

**Implementation:**
```typescript
const ALLOWED_MIME_TYPES = ['text/csv', 'application/vnd.ms-excel', ...];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_ROWS = 10000;

function validateUpload(file) {
  if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
    throw new ValidationError('Invalid file type');
  }
  if (file.size > MAX_FILE_SIZE) {
    throw new ValidationError('File too large');
  }
}
```

---

### 3.4 LLM Prompt Injection Prevention

**Requirements:**
- Treat all user input as untrusted
- Use structured prompts with clear delimiters
- Validate LLM outputs before storing
- Never execute code returned by LLM
- Limit LLM output length (max 50,000 tokens)

**Prompt Template Pattern:**
```
You are a construction codebook assistant.

<rules>
{user_provided_rules}
</rules>

<codebook_items>
{codebook_items_json}
</codebook_items>

<task>
Analyze the codebook and provide recommendations in JSON format.
</task>

<output_format>
{
  "recommendations": [...]
}
</output_format>
```

**Output Validation:**
- Parse JSON and validate against expected schema
- Reject responses with unexpected structure
- Sanitize text fields (remove script tags, SQL, etc.)

---

## 4. Secrets Management

### 4.1 Environment Variables

**Required Secrets:**
- `SUPABASE_SERVICE_KEY` - Supabase admin key
- `PINECONE_API_KEY` - Pinecone API key
- `LLM_API_KEY` - OpenAI/Anthropic API key
- `API_KEY_SIGNING_SECRET` - For signing/hashing API keys
- `JWT_PRIVATE_KEY` - For signing JWTs (if using JWT auth)

**Best Practices:**
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, Doppler)
- Rotate secrets every 90 days
- Never commit secrets to git
- Use different secrets for dev/staging/production
- Implement secret rotation without downtime

---

### 4.2 Database Credentials

**Requirements:**
- Use connection strings with SSL (`sslmode=require`)
- Rotate database passwords quarterly
- Use principle of least privilege (app user should NOT have DROP/ALTER)
- Enable Supabase Row Level Security (RLS) as additional layer

---

## 5. Data Protection

### 5.1 Encryption

**In Transit:**
- Require HTTPS/TLS 1.3 for all API requests
- Reject HTTP connections (redirect to HTTPS or return 400)
- Use HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

**At Rest:**
- Supabase provides encryption at rest by default
- Consider additional encryption for sensitive metadata fields
- Hash API keys and passwords (never store plaintext)

---

### 5.2 Data Retention & Deletion

**Soft Delete Policy:**
- Implement soft deletes for clients and codebooks
- Keep deleted data for 30 days before hard delete
- Provide "undelete" functionality within 30-day window

**Hard Delete (GDPR Compliance):**
- Provide endpoint for permanent data deletion: `DELETE /clients/{id}?permanent=true`
- Delete all associated data (codebooks, items, versions, audit logs)
- Delete Pinecone vectors
- Log deletion event
- Return confirmation

**Data Export (GDPR Right to Access):**
- Provide endpoint to export all client data in JSON format
- Include all codebooks, versions, items, recommendations, audit logs
- Exclude hashed API keys and internal IDs

---

### 5.3 Audit Logging

**Requirements:**
- Log all authentication attempts (success and failure)
- Log all data modifications (create, update, delete)
- Log all admin actions
- Log all API key usage
- Include: timestamp, user/API key, action, resource, client_id, IP address

**Sensitive Data:**
- Do NOT log API keys (log key prefix only)
- Do NOT log passwords
- Do NOT log full LLM responses (log token count and summary only)

---

## 6. Security Headers

Implement the following HTTP security headers:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## 7. Rate Limiting

### 7.1 API Rate Limits

**Per API Key:**
- Standard endpoints: 100 requests/minute
- LLM-heavy endpoints: 10 requests/hour
- File uploads: 5 uploads/hour

**Per IP Address (unauthenticated):**
- Authentication endpoint: 5 requests/minute (prevent brute force)

**Implementation:**
- Use Redis or in-memory store for rate limit counters
- Return `429 Too Many Requests` with headers:
  ```http
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 42
  X-RateLimit-Reset: 1610000000
  Retry-After: 60
  ```

---

### 7.2 LLM Cost Protection

**Requirements:**
- Track token usage per client in `llm_usage` table
- Set monthly token quotas per client
- Alert admins when client reaches 80% of quota
- Block requests when quota exceeded (return `402 Payment Required` or `429`)
- Provide endpoint for clients to view usage: `GET /clients/{id}/llm-usage/summary`

---

## 8. Security Testing

### 8.1 Automated Security Checks

**Pre-deployment:**
- Run static analysis (Semgrep, Snyk, npm audit)
- Check for known vulnerabilities in dependencies
- Scan Docker images for CVEs
- Run OWASP ZAP or Burp Suite for API security testing

**Runtime:**
- Enable Supabase security advisories
- Monitor for suspicious activity (unusual API usage patterns)
- Set up alerts for failed authentication attempts

---

### 8.2 Penetration Testing

**Before Production Launch:**
- Conduct manual penetration test
- Test for OWASP Top 10 vulnerabilities:
  1. Broken access control
  2. Cryptographic failures
  3. Injection
  4. Insecure design
  5. Security misconfiguration
  6. Vulnerable components
  7. Authentication failures
  8. Data integrity failures
  9. Logging failures
  10. SSRF

---

## 9. Incident Response

### 9.1 Security Breach Protocol

**If API key compromised:**
1. Immediately revoke the key
2. Notify the client
3. Audit all actions performed with the key
4. Check for data exfiltration
5. Generate new key for client

**If system breach detected:**
1. Isolate affected systems
2. Preserve logs and evidence
3. Notify affected clients within 72 hours (GDPR requirement)
4. Conduct forensic analysis
5. Patch vulnerabilities
6. Publish post-mortem

---

### 9.2 Bug Bounty Program (Future)

Consider launching a bug bounty program:
- Use platform like HackerOne or Bugcrowd
- Offer rewards for valid security findings
- Publish security policy at `/security.txt`

---

## 10. Compliance

### 10.1 GDPR Compliance

**Requirements:**
- Obtain consent for data processing
- Provide data export functionality
- Implement right to erasure (permanent delete)
- Notify users of breaches within 72 hours
- Maintain data processing records

---

### 10.2 SOC 2 Compliance (Future)

For enterprise customers, consider SOC 2 Type II certification:
- Implement comprehensive audit logging
- Encrypt all data at rest and in transit
- Regular security audits
- Incident response procedures
- Employee security training

---

## 11. Security Checklist

**Pre-launch:**
- [ ] All secrets stored in secrets manager (not .env files)
- [ ] API key authentication implemented and tested
- [ ] RBAC implemented with permission checks
- [ ] All queries scoped by client_id
- [ ] SQL injection testing passed
- [ ] File upload validation implemented
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] HTTPS enforced
- [ ] Audit logging enabled
- [ ] Dependency vulnerability scan clean
- [ ] Penetration test completed
- [ ] Incident response plan documented
- [ ] GDPR compliance requirements met

**Post-launch:**
- [ ] Monitor audit logs daily
- [ ] Review API key usage weekly
- [ ] Rotate secrets quarterly
- [ ] Update dependencies monthly
- [ ] Conduct security review quarterly
- [ ] Renew SSL certificates before expiration
