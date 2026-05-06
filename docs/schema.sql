-- Core dataset metadata
CREATE TABLE datasets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    file_path       VARCHAR(500) NOT NULL,
    file_format     VARCHAR(20) NOT NULL,  -- csv, excel, json, parquet
    file_size_bytes BIGINT,
    row_count       INTEGER,
    column_count    INTEGER,
    uploaded_by     VARCHAR(100),
    uploaded_at     TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    quality_score   FLOAT,                 -- 0-100
    status          VARCHAR(20) DEFAULT 'processing'  -- processing, ready, error
);

-- Column-level profiling results
CREATE TABLE column_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID REFERENCES datasets(id) ON DELETE CASCADE,
    column_name     VARCHAR(255) NOT NULL,
    column_index    INTEGER,
    raw_dtype       VARCHAR(50),           -- original pandas dtype
    inferred_type   VARCHAR(50),           -- monetary, person_name, date, email...
    missing_count   INTEGER,
    missing_pct     FLOAT,
    unique_count    INTEGER,
    mean            FLOAT,
    median          FLOAT,
    std_dev         FLOAT,
    min_value       VARCHAR(255),
    max_value       VARCHAR(255),
    distribution    VARCHAR(50),           -- normal, skewed, uniform...
    outlier_count   INTEGER,
    sample_values   JSONB,                 -- ["val1", "val2", ...]
    is_pii          BOOLEAN DEFAULT FALSE,
    pii_type        VARCHAR(50)            -- name, email, ssn, phone...
);

-- Auto-generated tags
CREATE TABLE dataset_tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID REFERENCES datasets(id) ON DELETE CASCADE,
    tag_category    VARCHAR(50),           -- domain, sensitivity, use_case, data_type
    tag_value       VARCHAR(100),
    confidence      FLOAT,                 -- 0.0 - 1.0
    method          VARCHAR(50)            -- zero_shot, ner, rule_based, manual
);

-- Quality score breakdown
CREATE TABLE quality_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID REFERENCES datasets(id) ON DELETE CASCADE,
    completeness    FLOAT,
    consistency     FLOAT,
    uniqueness      FLOAT,
    validity        FLOAT,
    timeliness      FLOAT,
    overall_score   FLOAT,
    scored_at       TIMESTAMP DEFAULT NOW()
);

-- Dashboard configuration (auto-generated)
CREATE TABLE dashboard_configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID REFERENCES datasets(id) ON DELETE CASCADE,
    config          JSONB NOT NULL,         -- chart types, columns, settings
    generated_at    TIMESTAMP DEFAULT NOW()
);

-- Search index metadata (vectors stored in ChromaDB/FAISS)
CREATE TABLE search_index (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID REFERENCES datasets(id) ON DELETE CASCADE,
    embedding_model VARCHAR(100),
    indexed_text    TEXT,                   -- concatenated searchable text
    indexed_at      TIMESTAMP DEFAULT NOW()
);