-- Construction Codebook AI Backend - MVP Schema
-- Run this in the Supabase SQL Editor

-- 1. clients
CREATE TABLE IF NOT EXISTS clients (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    slug text,
    contact_email text,
    metadata jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_clients_slug ON clients(slug) WHERE deleted_at IS NULL;

-- 2. codebooks
CREATE TABLE IF NOT EXISTS codebooks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name text NOT NULL,
    type text NOT NULL CHECK (type IN ('material', 'activity', 'bid_item')),
    description text,
    locked_by text,
    locked_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz
);
CREATE INDEX IF NOT EXISTS idx_codebooks_client ON codebooks(client_id, type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_codebooks_unique_name ON codebooks(client_id, name, type) WHERE deleted_at IS NULL;

-- 3. codebook_versions
CREATE TABLE IF NOT EXISTS codebook_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    codebook_id uuid NOT NULL REFERENCES codebooks(id) ON DELETE CASCADE,
    version_number int NOT NULL CHECK (version_number > 0),
    label text,
    notes text,
    rules_snapshot jsonb,
    analysis_summary text,
    analysis_details jsonb,
    prompt_version text,
    is_active boolean DEFAULT true,
    created_by text,
    created_at timestamptz DEFAULT now(),
    UNIQUE(codebook_id, version_number)
);
CREATE INDEX IF NOT EXISTS idx_versions_active ON codebook_versions(codebook_id, is_active);

-- 4. codebook_items
CREATE TABLE IF NOT EXISTS codebook_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id uuid NOT NULL REFERENCES codebook_versions(id) ON DELETE CASCADE,
    client_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    original_label text NOT NULL,
    description text,
    code text NOT NULL,
    application text CHECK (application IN ('sanitary_sewer', 'storm_sewer', 'water', 'other') OR application IS NULL),
    csi_division text,
    csi_section text,
    metadata jsonb,
    created_at timestamptz DEFAULT now(),
    UNIQUE(version_id, code)
);
CREATE INDEX IF NOT EXISTS idx_items_version ON codebook_items(version_id, code);
CREATE INDEX IF NOT EXISTS idx_items_client ON codebook_items(client_id, version_id);
CREATE INDEX IF NOT EXISTS idx_items_csi ON codebook_items(csi_division, csi_section);
CREATE INDEX IF NOT EXISTS idx_items_application ON codebook_items(application);

-- 5. jobs
CREATE TABLE IF NOT EXISTS jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    codebook_id uuid REFERENCES codebooks(id) ON DELETE SET NULL,
    job_type text NOT NULL CHECK (job_type IN ('initial_analysis', 'refactor', 'bulk_upload', 'semantic_search', 'export')),
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress int DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    result jsonb,
    error text,
    started_at timestamptz,
    completed_at timestamptz,
    created_at timestamptz DEFAULT now(),
    created_by text
);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(client_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_polling ON jobs(status, started_at);

-- Seed: Demo client
INSERT INTO clients (id, name, slug, contact_email)
VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Client', 'demo', 'demo@example.com')
ON CONFLICT (id) DO NOTHING;
