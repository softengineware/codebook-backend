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

3. **Job Queue & Workers**
   - **Job Queue** for async operations (LLM analysis, refactoring, large uploads)
   - **Worker processes** that poll and execute jobs
   - Job tracking via `jobs` table in Supabase
   - Retry logic with exponential backoff for transient failures

4. **Integration Clients**
   - **Supabase client** for SQL queries (via official SDK or Postgres driver).
   - **Pinecone client** for vector index operations.
   - **LLM client** for prompt construction and responses.

5. **Utilities**
   - CSV/Excel parsers
   - ID and timestamp helpers
   - Configuration loader for environment variables
   - Logging and error handling helpers

---

## 3. Request Flow Examples

### 3.1 First codebook upload (Async)

1. Client sends `POST /clients/{clientId}/codebooks/upload` with metadata and file/JSON.
2. API validates and parses input (basic validation only).
3. Service:
   - Creates `codebooks` row.
   - Creates a `jobs` row with `job_type='initial_analysis'` and `status='pending'`.
   - Writes an `audit_log` entry (`initial_import`).
4. API responds `202 Accepted` with `job_id`.
5. **Worker process** picks up the job and:
   - Updates job status to `running`.
   - Creates `codebook_versions` row (version 1).
   - Inserts `codebook_items` rows for each parsed item.
   - Generates embeddings for each item and upserts them into Pinecone.
   - Constructs an LLM prompt:
     - Codebook items
     - Any known preferences/rules
     - CSI context (pulled from Pinecone or a static reference dataset)
   - Receives analysis & recommendations from LLM.
   - Stores summary & details in `codebook_versions` and `codebook_recommendations`.
   - Updates job status to `completed` with result data.
   - Updates `audit_log` with completion details.
6. Client polls `GET /jobs/{jobId}` or receives webhook notification when complete.

### 3.2 Apply new coding rules / refactor (Async)

1. Client sends `POST /codebooks/{id}/rules` to define or update rules.
2. Service stores rules in `codebook_rules` and marks them active.
3. Client triggers `POST /codebooks/{id}/refactor`.
4. Service:
   - Validates no job is currently running for this codebook (check `locked_by` field).
   - Sets `codebooks.locked_by` to current user/job to prevent concurrent modifications.
   - Creates a `jobs` row with `job_type='refactor'` and `status='pending'`.
   - Writes an `audit_log` entry (`refactor_started`).
5. API responds `202 Accepted` with `job_id`.
6. **Worker process** picks up the job and:
   - Updates job status to `running`.
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
   - Updates job status to `completed`.
   - Clears `codebooks.locked_by` lock.
   - Logs the refactor completion in `audit_log`.
7. Client polls `GET /jobs/{jobId}` or receives webhook notification when complete.

### 3.3 Revert to previous version

1. Client requests `POST /codebooks/{id}/revert` with `targetVersionNumber`.
2. Service:
   - Loads the target version and its items.
   - Creates a new version whose items copy the target version.
   - Marks the new version as active (`is_active = true`).
   - Logs the revert in `audit_log`.
3. API returns the new version metadata (can be synchronous since it's just copying data).

---

## 4. Async Job Processing Architecture

### 4.1 Why Async?

**LLM operations are slow and can timeout HTTP requests:**
- Initial analysis: 10-30 seconds
- Refactoring large codebooks: 30-120 seconds
- Batch recommendations: 5-60 seconds

**Benefits of async processing:**
- No HTTP request timeouts
- Better user experience (show progress)
- Retry failed operations automatically
- Scale workers independently from API servers
- Handle large uploads without blocking API

---

### 4.2 Job Queue Implementation Options

#### Option 1: Database-backed Queue (Simple, Recommended for MVP)

Use the `jobs` table in Supabase as the queue:

**Advantages:**
- No additional infrastructure
- Strong consistency (ACID transactions)
- Easy to query job status
- Built-in persistence

**Disadvantages:**
- Not ideal for very high throughput (>1000 jobs/sec)
- Requires polling

**Implementation:**
```typescript
// Job creation (API layer)
async function createJob(clientId, codebookId, jobType, payload) {
  const job = await supabase.from('jobs').insert({
    client_id: clientId,
    codebook_id: codebookId,
    job_type: jobType,
    status: 'pending',
    result: payload
  }).select().single();

  return job;
}

// Worker polling loop
async function pollAndProcessJobs() {
  while (true) {
    const { data: jobs } = await supabase
      .from('jobs')
      .select('*')
      .eq('status', 'pending')
      .order('created_at', { ascending: true })
      .limit(10);

    for (const job of jobs) {
      await processJob(job);
    }

    await sleep(5000); // Poll every 5 seconds
  }
}

// Job processing
async function processJob(job) {
  // Mark as running (with optimistic locking)
  const { error } = await supabase
    .from('jobs')
    .update({
      status: 'running',
      started_at: new Date().toISOString()
    })
    .eq('id', job.id)
    .eq('status', 'pending'); // Only update if still pending

  if (error) return; // Another worker picked it up

  try {
    let result;
    switch (job.job_type) {
      case 'initial_analysis':
        result = await processInitialAnalysis(job);
        break;
      case 'refactor':
        result = await processRefactor(job);
        break;
      case 'bulk_upload':
        result = await processBulkUpload(job);
        break;
    }

    await supabase
      .from('jobs')
      .update({
        status: 'completed',
        result,
        completed_at: new Date().toISOString()
      })
      .eq('id', job.id);

  } catch (error) {
    await supabase
      .from('jobs')
      .update({
        status: 'failed',
        error: error.message,
        completed_at: new Date().toISOString()
      })
      .eq('id', job.id);

    // Implement retry logic
    if (job.retry_count < 3) {
      await retryJob(job);
    }
  }
}
```

---

#### Option 2: Redis-backed Queue (Better Performance)

Use Bull (Node.js) or RQ (Python) with Redis:

**Advantages:**
- High throughput
- Built-in retry logic
- Job priority support
- Delayed jobs
- Event-based (no polling)

**Disadvantages:**
- Additional infrastructure (Redis)
- Job data stored separately from application data

**Implementation (Bull):**
```typescript
import Queue from 'bull';

const jobQueue = new Queue('codebook-jobs', {
  redis: {
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT
  }
});

// API layer: Add job to queue
async function createAnalysisJob(clientId, codebookId, items) {
  const job = await jobQueue.add('initial_analysis', {
    client_id: clientId,
    codebook_id: codebookId,
    items
  }, {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000
    }
  });

  // Also create job record in database for querying
  await supabase.from('jobs').insert({
    id: job.id,
    client_id: clientId,
    codebook_id: codebookId,
    job_type: 'initial_analysis',
    status: 'pending'
  });

  return job.id;
}

// Worker: Process jobs
jobQueue.process('initial_analysis', async (job) => {
  await updateJobStatus(job.id, 'running');

  try {
    const result = await processInitialAnalysis(job.data);
    await updateJobStatus(job.id, 'completed', result);
    return result;
  } catch (error) {
    await updateJobStatus(job.id, 'failed', null, error.message);
    throw error; // Bull will retry
  }
});
```

---

#### Option 3: Cloud-native Queue (AWS SQS, Google Cloud Tasks)

**Advantages:**
- Fully managed
- Auto-scaling
- High reliability
- Dead letter queues

**Disadvantages:**
- Vendor lock-in
- Additional cost
- More complex setup

---

### 4.3 Job Retry Strategy

**Retry Policy:**
- Retry failed jobs up to 3 times
- Use exponential backoff: 2s, 4s, 8s
- Retry on transient errors:
  - LLM API rate limits (429)
  - LLM API timeouts (504)
  - Pinecone connection errors (503)
  - Database connection errors (503)

**Do NOT retry on:**
- Invalid input (400, 422)
- Authorization errors (403)
- Resource not found (404)
- LLM API quota exceeded (402)

**Implementation:**
```typescript
function isRetryableError(error) {
  const retryableStatusCodes = [429, 502, 503, 504];
  return retryableStatusCodes.includes(error.status);
}

async function processJobWithRetry(job, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await processJob(job);
    } catch (error) {
      if (!isRetryableError(error) || attempt === maxRetries) {
        throw error;
      }

      const delayMs = Math.pow(2, attempt) * 1000;
      await sleep(delayMs);

      // Update job with retry attempt
      await supabase
        .from('jobs')
        .update({ retry_count: attempt })
        .eq('id', job.id);
    }
  }
}
```

---

### 4.4 Progress Reporting

For long-running jobs, update progress periodically:

```typescript
async function processRefactor(job) {
  const items = await getCodebookItems(job.codebook_id);
  const totalItems = items.length;

  for (let i = 0; i < items.length; i += 100) {
    const batch = items.slice(i, i + 100);

    // Process batch
    await refactorBatch(batch);

    // Update progress
    const progress = Math.floor(((i + batch.length) / totalItems) * 100);
    await supabase
      .from('jobs')
      .update({ progress })
      .eq('id', job.id);
  }
}
```

**Client polling:**
```typescript
async function waitForJobCompletion(jobId) {
  while (true) {
    const { data: job } = await fetch(`/jobs/${jobId}`).then(r => r.json());

    if (job.status === 'completed') {
      return job.result;
    } else if (job.status === 'failed') {
      throw new Error(job.error);
    }

    console.log(`Job progress: ${job.progress}%`);
    await sleep(2000); // Poll every 2 seconds
  }
}
```

---

### 4.5 Worker Scaling

**Horizontal Scaling:**
- Run multiple worker processes on different servers
- Each worker polls the job queue
- Use optimistic locking to prevent duplicate processing
- Scale based on queue depth:
  - Queue depth > 100: Scale up
  - Queue depth < 10: Scale down

**Vertical Scaling:**
- Increase CPU/memory for LLM-heavy operations
- Use separate worker pools for different job types:
  - Fast workers: Semantic search, exports
  - Heavy workers: Initial analysis, refactor

**Kubernetes Autoscaling:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: codebook-worker
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codebook-worker
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: External
    external:
      metric:
        name: job_queue_depth
      target:
        type: AverageValue
        averageValue: "50"
```

---

### 4.6 Job Monitoring & Alerting

**Metrics to track:**
- Jobs created per minute
- Jobs completed per minute
- Job success rate (%)
- Job failure rate (%)
- Average job duration by type
- Queue depth (pending jobs)
- Worker utilization (%)

**Alerts:**
- Queue depth > 500 for 10 minutes (scale up workers)
- Job failure rate > 10% for 5 minutes (investigate errors)
- Job duration p95 > 5 minutes (LLM performance issue)
- No jobs completed in 10 minutes (worker health check)

---

### 4.7 Dead Letter Queue

For jobs that fail after all retries, move to dead letter queue for manual investigation:

```typescript
async function handleFailedJob(job) {
  if (job.retry_count >= 3) {
    // Move to dead letter queue
    await supabase.from('failed_jobs').insert({
      job_id: job.id,
      client_id: job.client_id,
      codebook_id: job.codebook_id,
      job_type: job.job_type,
      error: job.error,
      payload: job.result,
      failed_at: new Date().toISOString()
    });

    // Notify admin
    await sendAlert({
      type: 'job_failed',
      job_id: job.id,
      error: job.error
    });
  }
}
```

---

### 4.8 Graceful Shutdown

Handle SIGTERM/SIGINT for graceful worker shutdown:

```typescript
let isShuttingDown = false;

process.on('SIGTERM', async () => {
  isShuttingDown = true;
  console.log('Received SIGTERM, finishing current jobs...');

  // Stop accepting new jobs
  // Wait for current jobs to complete (with timeout)
  await Promise.race([
    waitForCurrentJobs(),
    sleep(30000) // 30 second grace period
  ]);

  console.log('Shutdown complete');
  process.exit(0);
});

async function pollAndProcessJobs() {
  while (!isShuttingDown) {
    // ... poll and process
  }
}
```

---

## 5. Pinecone Strategy

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

## 6. LLM Usage Patterns

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

## 7. Configuration

Example environment variables (see `.env.example`):

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`
- `PINECONE_ENVIRONMENT` (if applicable)
- `LLM_API_KEY`
- `LLM_MODEL_NAME`
- `APP_ENV` (e.g. `development`, `production`)
- `REDIS_HOST` (optional, for Redis-backed job queue)
- `REDIS_PORT` (optional)

Configuration is loaded once at startup and passed to integration clients.

---

## 8. Future Extensions

- Role-based access control (consultant vs. client users) - see SECURITY.md for specifications.
- Per-client Pinecone namespaces or per-codebook indexes.
- UI dashboard for visualizing structure, CSI mapping, and version diffs.
- Export formats for HCSS or other estimating systems.
- Webhook notifications for job completion (currently client polling only).
- Real-time progress updates via WebSockets/Server-Sent Events.
