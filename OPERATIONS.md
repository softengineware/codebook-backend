# Operations Guide

This document covers monitoring, logging, deployment, backup, and operational procedures for the Construction Codebook AI Backend.

---

## 1. Monitoring & Observability

### 1.1 Health Checks

#### Application Health Endpoint
```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.2.3",
  "checks": {
    "database": "healthy",
    "pinecone": "healthy",
    "llm_service": "healthy"
  }
}
```

**Health Check Logic:**
- Database: Run simple query (`SELECT 1`)
- Pinecone: Check index stats API
- LLM Service: Verify API key validity (don't make expensive call)

**Status Codes:**
- `200` - All systems healthy
- `503` - One or more systems degraded/unhealthy

**Kubernetes Liveness/Readiness:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

### 1.2 Application Metrics

#### Key Metrics to Track

**Request Metrics:**
- Total requests per second (RPS)
- Request latency (p50, p95, p99)
- Error rate (% of 4xx and 5xx responses)
- Request by endpoint
- Request by client_id

**Business Metrics:**
- Codebooks created per day
- Items uploaded per day
- Refactor operations completed per day
- LLM tokens consumed per hour/day
- Recommendations generated per day
- Recommendation acceptance rate

**System Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Active database connections
- Job queue depth

**External Service Metrics:**
- Supabase query latency
- Pinecone operation latency (upsert, query)
- LLM API latency
- LLM API error rate
- Token usage per LLM call

---

### 1.3 Monitoring Stack Options

#### Option 1: Prometheus + Grafana
```yaml
# docker-compose.yml excerpt
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=secret
```

**Metrics Export:**
- Use Prometheus client library
- Expose metrics endpoint: `GET /metrics`
- Track custom metrics (codebooks created, LLM tokens, etc.)

#### Option 2: Datadog
- Install Datadog agent on servers
- Use Datadog APM for request tracing
- Custom metrics via StatsD or Datadog API

#### Option 3: New Relic
- Install New Relic agent
- Automatic instrumentation of HTTP requests
- Custom transactions for background jobs

---

### 1.4 Alerting Rules

**Critical Alerts (Page on-call):**
- Error rate > 5% for 5 minutes
- API latency p95 > 5 seconds for 5 minutes
- Database connection pool exhausted
- Disk space < 10% free
- Any external service down (Supabase, Pinecone, LLM)

**Warning Alerts (Email/Slack):**
- Error rate > 2% for 10 minutes
- Job queue depth > 100
- LLM API error rate > 10% for 10 minutes
- Client approaching LLM token quota (80%)
- SSL certificate expiring within 30 days

**Example Alert (Prometheus):**
```yaml
groups:
  - name: codebook_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} for endpoint {{ $labels.endpoint }}"
```

---

## 2. Logging

### 2.1 Log Levels

Use standard log levels:
- **ERROR** - Application errors, exceptions
- **WARN** - Recoverable errors, deprecations, rate limits
- **INFO** - Important business events (codebook created, job completed)
- **DEBUG** - Detailed diagnostic information

**Production:** INFO and above
**Development:** DEBUG and above

---

### 2.2 Structured Logging

Use JSON format for all logs:

```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "level": "INFO",
  "message": "Codebook created successfully",
  "context": {
    "request_id": "uuid",
    "client_id": "uuid",
    "codebook_id": "uuid",
    "user_id": "user@example.com",
    "endpoint": "POST /clients/:clientId/codebooks",
    "latency_ms": 245,
    "status_code": 201
  }
}
```

**Required Fields:**
- `timestamp` - ISO 8601 with milliseconds
- `level` - Log level
- `message` - Human-readable message
- `request_id` - Correlation ID for tracing requests across services
- `client_id` - For multi-tenant filtering

---

### 2.3 What to Log

**DO Log:**
- All API requests (method, path, status, latency)
- Authentication attempts (success and failure)
- Authorization failures (403s)
- Database query errors
- External API errors (Pinecone, LLM)
- Job lifecycle (created, started, completed, failed)
- LLM token usage (per request)
- Rate limit violations

**DO NOT Log:**
- API keys (log prefix only, e.g., `ck_live_1234...`)
- Passwords
- Full LLM prompts/responses (log summaries only)
- Sensitive PII unless required for debugging

---

### 2.4 Log Aggregation

#### Option 1: ELK Stack (Elasticsearch, Logstash, Kibana)
```yaml
# docker-compose.yml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  environment:
    - discovery.type=single-node
  ports:
    - "9200:9200"

kibana:
  image: docker.elastic.co/kibana/kibana:8.11.0
  ports:
    - "5601:5601"

logstash:
  image: docker.elastic.co/logstash/logstash:8.11.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
```

#### Option 2: CloudWatch Logs (AWS)
- Configure CloudWatch Logs agent
- Use log groups per service
- Set retention policies (30 days for debug, 1 year for audit)

#### Option 3: Datadog Logs
- Forward logs to Datadog
- Use tags for filtering (env, service, client_id)

---

### 2.5 Log Retention

**Retention Policies:**
- Application logs: 30 days
- Audit logs: 7 years (compliance requirement)
- Error logs: 90 days
- Debug logs: 7 days

**Archive to S3/GCS after retention period for compliance.**

---

## 3. Deployment

### 3.1 Deployment Platforms

#### Option 1: Docker + Kubernetes
```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 8000
CMD ["node", "dist/index.js"]
```

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codebook-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codebook-backend
  template:
    metadata:
      labels:
        app: codebook-backend
    spec:
      containers:
      - name: api
        image: codebook-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: NODE_ENV
          value: "production"
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: codebook-secrets
              key: supabase-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

#### Option 2: Platform-as-a-Service

**Render:**
```yaml
# render.yaml
services:
  - type: web
    name: codebook-backend
    env: node
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: SUPABASE_URL
        sync: false
```

**Railway / Fly.io:**
- Connect GitHub repository
- Auto-deploy on push to main
- Configure environment variables in dashboard

**AWS Elastic Beanstalk:**
- Deploy Docker container or source code
- Managed scaling and load balancing

---

### 3.2 CI/CD Pipeline

#### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      - run: npm run lint

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run security scan
        run: npm audit --audit-level=high

  deploy:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t codebook-backend:${{ github.sha }} .
      - name: Push to registry
        run: docker push codebook-backend:${{ github.sha }}
      - name: Deploy to Kubernetes
        run: kubectl set image deployment/codebook-backend api=codebook-backend:${{ github.sha }}
```

---

### 3.3 Database Migrations

#### Migration Tool Setup

**Node/TypeScript (Prisma):**
```bash
npx prisma migrate dev --name add_jobs_table
npx prisma migrate deploy  # Production
```

**Python (Alembic):**
```bash
alembic revision -m "add jobs table"
alembic upgrade head  # Production
```

**Supabase Migrations:**
```bash
supabase migration new add_jobs_table
# Edit migrations/YYYYMMDD_add_jobs_table.sql
supabase db push  # Apply to remote
```

#### Migration Best Practices

**Pre-deployment:**
1. Test migrations on staging database
2. Backup production database before migration
3. Verify rollback procedure works

**During deployment:**
1. Run migrations before deploying new code
2. Use transactional DDL where possible
3. Avoid long-running migrations (lock tables)

**Rollback Plan:**
- Keep rollback SQL for each migration
- Version migrations (YYYYMMDD_HHMMSS_name.sql)
- Document breaking changes

**Example Migration:**
```sql
-- migrations/20250115_add_jobs_table.sql
BEGIN;

CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  job_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_jobs_status ON jobs(status, started_at);

COMMIT;
```

**Rollback:**
```sql
-- rollback/20250115_add_jobs_table.sql
DROP TABLE IF EXISTS jobs;
```

---

### 3.4 Blue-Green Deployment

**Strategy:**
1. Deploy new version to "green" environment
2. Run smoke tests on green
3. Switch traffic from blue to green
4. Monitor for errors
5. Keep blue running for quick rollback

**Load Balancer Configuration:**
```nginx
upstream backend {
  server blue.backend.internal:8000 weight=100;
  server green.backend.internal:8000 weight=0;
}

# After validation, update weights:
# blue weight=0, green weight=100
```

---

## 4. Backup & Disaster Recovery

### 4.1 Database Backups

#### Supabase Backups

**Automatic:**
- Supabase provides daily automatic backups
- Retention: 7 days (free tier), 30 days (pro)
- Enable Point-in-Time Recovery (PITR) for pro plans

**Manual Backups:**
```bash
# Backup before major changes
pg_dump -h db.supabase.co -U postgres -d codebook > backup-$(date +%Y%m%d).sql

# Restore
psql -h db.supabase.co -U postgres -d codebook < backup-20250115.sql
```

**Backup Schedule:**
- Daily automatic backups (retained 30 days)
- Weekly manual backups (retained 90 days, stored in S3)
- Before each deployment
- Before running risky migrations

---

### 4.2 Pinecone Backups

**Strategy:**
Pinecone doesn't support native backups. Implement application-level backup:

```typescript
// Backup script
async function backupPineconeIndex() {
  const allVectors = await pinecone.index('codebooks').fetch({
    ids: await getAllVectorIds()
  });

  await s3.putObject({
    Bucket: 'codebook-backups',
    Key: `pinecone-backup-${Date.now()}.json`,
    Body: JSON.stringify(allVectors)
  });
}
```

**Schedule:** Weekly backups of Pinecone index

**Recovery:**
1. Create new Pinecone index
2. Re-upsert vectors from backup JSON
3. Update application config to use new index

---

### 4.3 Disaster Recovery Plan

#### RTO and RPO Goals

- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 24 hours (max data loss)

#### Disaster Scenarios

**Scenario 1: Database Corruption**
1. Stop application (prevent further writes)
2. Restore from most recent backup
3. Verify data integrity
4. Resume application
5. Notify affected clients if data loss occurred

**Scenario 2: Complete Infrastructure Failure**
1. Provision new infrastructure (Kubernetes cluster, etc.)
2. Restore database from backup
3. Deploy application from last known good version
4. Restore Pinecone index from backup
5. Update DNS to point to new infrastructure
6. Validate all services healthy

**Scenario 3: Data Breach**
1. Follow Security Incident Response (see SECURITY.md)
2. Isolate affected systems
3. Audit all data access in audit logs
4. Revoke compromised API keys
5. Notify affected clients within 72 hours

---

### 4.4 Backup Testing

**Monthly:**
- Perform test restore of database backup
- Verify data integrity
- Document time to restore

**Quarterly:**
- Full disaster recovery drill
- Restore entire stack from backups
- Measure actual RTO vs. target

---

## 5. Performance Optimization

### 5.1 Database Query Optimization

**Monitoring:**
- Enable Supabase slow query log (queries > 1 second)
- Review query plans with `EXPLAIN ANALYZE`

**Optimization Techniques:**
- Add indexes for frequently filtered columns
- Use materialized views for expensive aggregations
- Implement database connection pooling (PgBouncer)
- Cache frequently accessed data (Redis)

**Example: Slow Query**
```sql
-- Slow
SELECT * FROM codebook_items WHERE client_id = '...' ORDER BY created_at DESC;

-- Add index
CREATE INDEX idx_items_client_created ON codebook_items(client_id, created_at DESC);
```

---

### 5.2 Caching Strategy

**What to Cache:**
- Active codebook versions (cache for 5 minutes)
- Client rules (cache for 10 minutes)
- CSI division reference data (cache for 1 hour)
- LLM prompt templates (cache indefinitely, invalidate on update)

**Cache Implementation (Redis):**
```typescript
async function getActiveVersion(codebookId: string) {
  const cacheKey = `codebook:${codebookId}:active_version`;
  const cached = await redis.get(cacheKey);

  if (cached) {
    return JSON.parse(cached);
  }

  const version = await db.query(`
    SELECT * FROM codebook_versions
    WHERE codebook_id = $1 AND is_active = true
  `, [codebookId]);

  await redis.setex(cacheKey, 300, JSON.stringify(version)); // Cache 5 min
  return version;
}
```

**Cache Invalidation:**
- Invalidate on codebook update
- Use cache tags for bulk invalidation
- Set reasonable TTLs

---

### 5.3 API Response Compression

Enable gzip/brotli compression:

```typescript
// Express example
import compression from 'compression';
app.use(compression());
```

---

### 5.4 Pagination Best Practices

**Use cursor-based pagination** for large datasets:

```sql
-- Cursor-based (efficient)
SELECT * FROM codebook_items
WHERE client_id = $1 AND id > $2
ORDER BY id
LIMIT 100;

-- Offset-based (inefficient for large offsets)
SELECT * FROM codebook_items
WHERE client_id = $1
ORDER BY id
OFFSET 10000 LIMIT 100;  -- Slow!
```

---

## 6. Cost Management

### 6.1 LLM Cost Tracking

**Monitor:**
- Token usage per client (via `llm_usage` table)
- Most expensive operations (refactor > analysis > search)
- Monthly spend by client and model

**Alerts:**
- Client exceeds 80% of monthly quota
- Total monthly spend exceeds budget

**Optimization:**
- Use cheaper models for simple tasks (GPT-4o-mini instead of GPT-4o)
- Cache LLM responses for identical prompts
- Set max_tokens limits

---

### 6.2 Infrastructure Cost

**Optimize:**
- Right-size compute instances (use monitoring data)
- Use auto-scaling during low-traffic periods
- Schedule background jobs during off-peak hours
- Archive old data to cheaper storage (S3 Glacier)

---

## 7. Maintenance Windows

### 7.1 Scheduled Maintenance

**Frequency:** Monthly (first Saturday, 2-6 AM UTC)

**Tasks:**
- Apply security patches
- Update dependencies
- Run database maintenance (VACUUM, REINDEX)
- Rotate secrets
- Review and archive old logs

**Communication:**
- Email clients 7 days in advance
- Display banner on dashboard 24 hours before
- Send reminder 1 hour before maintenance

---

### 7.2 Emergency Maintenance

**Triggers:**
- Critical security vulnerability
- Database performance degradation
- External service outage requiring failover

**Process:**
1. Assess severity and impact
2. Notify clients immediately if downtime expected
3. Implement fix
4. Validate in staging
5. Deploy to production
6. Send post-mortem report within 24 hours

---

## 8. Runbook: Common Issues

### Issue: High Database CPU

**Symptoms:** Slow API responses, database connection timeouts

**Diagnosis:**
1. Check Supabase dashboard for slow queries
2. Run `SELECT * FROM pg_stat_activity WHERE state = 'active';`
3. Identify long-running queries

**Resolution:**
1. Add missing indexes
2. Optimize queries
3. Increase connection pool size if needed
4. Scale database (vertical or horizontal)

---

### Issue: Job Queue Backlog

**Symptoms:** Jobs stuck in 'pending' status, users reporting slow refactors

**Diagnosis:**
1. Check job queue depth: `SELECT COUNT(*) FROM jobs WHERE status = 'pending';`
2. Check for failed workers
3. Review error logs

**Resolution:**
1. Scale up worker instances
2. Investigate failed jobs (check error messages)
3. Retry failed jobs if transient error
4. Increase job timeout if LLM calls are slow

---

### Issue: LLM API Errors

**Symptoms:** 500 errors on refactor/analysis endpoints, "LLM service unavailable"

**Diagnosis:**
1. Check LLM provider status page
2. Review error logs for API error codes
3. Test API key validity

**Resolution:**
1. Implement retry with exponential backoff
2. Use fallback LLM provider if available
3. Queue jobs for retry when service recovers
4. Notify users of temporary degradation

---

## 9. On-Call Procedures

### On-Call Rotation

- Primary on-call: 24/7 coverage
- Secondary on-call: Escalation backup
- Rotation: Weekly

### Alert Response SLAs

- **Critical (P0):** Acknowledge within 15 minutes, resolve within 4 hours
- **High (P1):** Acknowledge within 1 hour, resolve within 24 hours
- **Medium (P2):** Acknowledge within 4 hours, resolve within 3 days

### Escalation Path

1. Primary on-call engineer
2. Secondary on-call engineer
3. Engineering manager
4. CTO

---

## 10. Documentation

### Operational Docs Checklist

- [ ] Architecture diagram
- [ ] Deployment procedure
- [ ] Rollback procedure
- [ ] Database migration guide
- [ ] Disaster recovery plan
- [ ] On-call runbook
- [ ] API documentation
- [ ] Monitoring dashboard links
- [ ] Secrets location and rotation procedure
- [ ] Vendor contact information (Supabase, Pinecone, LLM provider)
