-- Finance AI SaaS Core Schema

-- 1. Documents Table: Stores metadata about uploaded financial files
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_by UUID NOT NULL, -- Links to auth.users in Supabase
    organization_id UUID NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path TEXT NOT NULL, -- Path in Supabase Storage
    document_type TEXT, -- 10-K, 10-Q, etc.
    company_name TEXT,
    fiscal_period TEXT,
    currency TEXT DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Extractions Table: Stores the results of the agentic pipeline
CREATE TABLE IF NOT EXISTS extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    extraction_id UUID NOT NULL UNIQUE, -- The ID returned to the user
    status TEXT NOT NULL DEFAULT 'processing', -- processing, completed, failed
    quality_score FLOAT DEFAULT 0,
    selected_agent TEXT NOT NULL,
    structured_data JSONB NOT NULL DEFAULT '{}', -- The full ExtractionResult object
    errors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Audit Logs: Immutable record of all data operations
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    action TEXT NOT NULL, -- read, write, update, delete
    resource_type TEXT NOT NULL, -- document, extraction
    resource_id UUID NOT NULL,
    context JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_documents_org ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_extractions_doc ON extractions(document_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource ON audit_logs(resource_id);
