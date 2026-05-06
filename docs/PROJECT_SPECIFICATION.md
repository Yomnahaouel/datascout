# DataScout — Complete Project Specification
# AI-Powered Smart Data Catalogue for Banking

## PURPOSE OF THIS DOCUMENT
This document is the complete specification for the DataScout project. It is intended to be read by an AI assistant (Claude/GPT) to help build the entire application from scratch. It contains everything needed: what the project does, how it works, what technologies to use, what AI models to use, the database schema, API endpoints, frontend pages, and the full architecture. Follow this document as the single source of truth for building DataScout.

---

## WHAT IS DATASCOUT

DataScout is a web application that acts as a smart data catalogue. Users upload datasets (CSV, Excel, JSON), and the system automatically:
1. Profiles the dataset (column types, statistics, distributions, outliers, correlations)
2. Tags the dataset (domain classification like Finance/HR/Risk, and PII detection like names/emails/SSNs)
3. Scores the dataset quality (0–100 across 5 dimensions)
4. Indexes the dataset for semantic search (converts metadata to vectors for natural language search)
5. Generates an exploratory dashboard (auto-selects relevant charts based on the data profile)

After processing, any user can search the catalogue using natural language queries (e.g., "fraud detection data for credit cards") and instantly find, understand, and visualize relevant datasets.

The domain focus is banking (transactions, clients, credit, fraud, risk) but the architecture is domain-agnostic.

---

## TECH STACK

| Layer | Technology | Version |
|---|---|---|
| Frontend | React + TypeScript | React 18+ |
| Styling | Tailwind CSS | 3+ |
| Charts | Recharts | Latest |
| Backend | FastAPI (Python) | Python 3.11+ |
| Relational Database | PostgreSQL | 15+ |
| Vector Database | ChromaDB | Latest |
| AI - Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Latest |
| AI - Zero-shot Classification | facebook/bart-large-mnli (via HuggingFace transformers) | Latest |
| AI - NER (PII Detection) | spaCy (en_core_web_sm) | 3+ |
| AI - Outlier Detection | scikit-learn (IsolationForest) | Latest |
| Data Processing | pandas, numpy, scipy | Latest |
| Synthetic Data | Faker | Latest |
| Containerization | Docker + Docker Compose | Latest |
| Version Control | Git + GitHub | — |

---

## PROJECT STRUCTURE

```
datascout/
├── docker-compose.yml
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                          # FastAPI app entry point
│   ├── config.py                        # Environment variables, DB connection strings
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_datasets.py           # CRUD endpoints for datasets
│   │   ├── routes_search.py             # Semantic search endpoint
│   │   ├── routes_profile.py            # Profiling endpoints
│   │   ├── routes_tags.py               # Tagging endpoints
│   │   ├── routes_quality.py            # Quality score endpoints
│   │   └── routes_dashboard.py          # Dashboard config endpoint
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── database_models.py           # SQLAlchemy ORM models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── pydantic_schemas.py          # Pydantic request/response schemas
│   │
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── search_engine.py             # Semantic search (sentence-transformers + ChromaDB)
│   │   ├── profiler_engine.py           # Auto-profiler (pandas + scipy + IsolationForest)
│   │   ├── tagger_engine.py             # Auto-tagger (BART zero-shot + spaCy NER + regex)
│   │   ├── quality_engine.py            # Quality scorer (rule-based, 5 dimensions)
│   │   └── dashboard_engine.py          # Dashboard generator (chart selection logic)
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── ingestion.py                 # Orchestrates the full pipeline on upload
│   │
│   └── db/
│       ├── __init__.py
│       ├── database.py                  # Database connection and session
│       └── init_db.py                   # Create tables on startup
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   │
│   ├── public/
│   │   └── index.html
│   │
│   └── src/
│       ├── App.tsx                      # Main app with routing
│       ├── index.tsx                    # Entry point
│       │
│       ├── pages/
│       │   ├── SearchPage.tsx           # Search bar + results
│       │   ├── BrowsePage.tsx           # Browse all datasets with filters
│       │   ├── DatasetProfilePage.tsx   # Full profile of a single dataset
│       │   └── DashboardPage.tsx        # Auto-generated dashboard for a dataset
│       │
│       ├── components/
│       │   ├── SearchBar.tsx
│       │   ├── DatasetCard.tsx          # Card showing dataset summary
│       │   ├── QualityBadge.tsx         # Quality score visual (0-100)
│       │   ├── TagList.tsx              # Display tags
│       │   ├── ProfileTable.tsx         # Column-level profile table
│       │   ├── KPICards.tsx             # Row count, col count, size, quality
│       │   ├── HistogramChart.tsx
│       │   ├── BarChartComponent.tsx
│       │   ├── PieChartComponent.tsx
│       │   ├── BoxPlotChart.tsx
│       │   ├── TimeSeriesChart.tsx
│       │   ├── HeatmapChart.tsx
│       │   ├── MissingValuesMap.tsx
│       │   └── ClassBalanceChart.tsx
│       │
│       ├── services/
│       │   └── api.ts                   # Axios/fetch calls to backend
│       │
│       └── types/
│           └── types.ts                 # TypeScript interfaces
│
└── data/
    ├── datasets/                        # Uploaded dataset files stored here
    └── synthetic/                       # Generated synthetic datasets
        └── generate_synthetic.py        # Script to generate synthetic datasets
```

---

## DATABASE SCHEMA (PostgreSQL)

```sql
-- Core dataset metadata
CREATE TABLE datasets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    file_path       VARCHAR(500) NOT NULL,
    file_format     VARCHAR(20) NOT NULL,
    file_size_bytes BIGINT,
    row_count       INTEGER,
    column_count    INTEGER,
    uploaded_at     TIMESTAMP DEFAULT NOW(),
    quality_score   FLOAT,
    status          VARCHAR(20) DEFAULT 'processing'
);

-- Column-level profiling results
CREATE TABLE column_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID REFERENCES datasets(id) ON DELETE CASCADE,
    column_name     VARCHAR(255) NOT NULL,
    column_index    INTEGER,
    raw_dtype       VARCHAR(50),
    inferred_type   VARCHAR(50),
    missing_count   INTEGER,
    missing_pct     FLOAT,
    unique_count    INTEGER,
    mean            FLOAT,
    median          FLOAT,
    std_dev         FLOAT,
    min_value       VARCHAR(255),
    max_value       VARCHAR(255),
    distribution    VARCHAR(50),
    outlier_count   INTEGER,
    sample_values   JSONB,
    is_pii          BOOLEAN DEFAULT FALSE,
    pii_type        VARCHAR(50)
);

-- Auto-generated tags
CREATE TABLE dataset_tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID REFERENCES datasets(id) ON DELETE CASCADE,
    tag_category    VARCHAR(50),
    tag_value       VARCHAR(100),
    confidence      FLOAT,
    method          VARCHAR(50)
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

-- Dashboard configuration
CREATE TABLE dashboard_configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID REFERENCES datasets(id) ON DELETE CASCADE,
    config          JSONB NOT NULL,
    generated_at    TIMESTAMP DEFAULT NOW()
);
```

---

## API ENDPOINTS

```
POST   /api/datasets/upload              Upload a new dataset file
GET    /api/datasets                     List all datasets (supports filters: domain, quality, format)
GET    /api/datasets/{id}                Get full dataset details (metadata + profile + tags + quality)
DELETE /api/datasets/{id}                Delete a dataset
GET    /api/datasets/{id}/preview        Preview first 50 rows of the dataset

GET    /api/search?q={query}             Semantic search — returns ranked datasets

GET    /api/datasets/{id}/profile        Get full column-level profile
GET    /api/datasets/{id}/tags           Get all tags for a dataset
GET    /api/datasets/{id}/quality        Get quality score breakdown
GET    /api/datasets/{id}/dashboard      Get dashboard config (JSON with chart types and data)
```

---

## ENGINE SPECIFICATIONS

### ENGINE 1: SEMANTIC SEARCH (search_engine.py)

Purpose: Let users find datasets by typing natural language queries.

How it works:
1. When a dataset is uploaded, concatenate its name + description + column names + tag values into one text string.
2. Use the sentence-transformers model "all-MiniLM-L6-v2" to convert that text into a 384-dimensional vector.
3. Store the vector in ChromaDB with the dataset ID as metadata.
4. When a user searches, convert the query into a vector using the same model.
5. Query ChromaDB for the top N most similar vectors (cosine similarity).
6. Return the matching dataset IDs with similarity scores.

Implementation details:
- Use the "sentence-transformers" Python library.
- Use ChromaDB as the vector store. Create one collection called "dataset_embeddings".
- On upload: call collection.add(documents=[text], embeddings=[vector], ids=[dataset_id]).
- On search: call collection.query(query_embeddings=[query_vector], n_results=10).
- Return results sorted by similarity score (highest first).

### ENGINE 2: AUTO-PROFILER (profiler_engine.py)

Purpose: Analyze every column of a dataset and produce a complete statistical profile.

How it works:
1. Read the dataset into a pandas DataFrame.
2. For each column, compute:
   - raw_dtype: the pandas dtype (int64, float64, object, datetime64, bool).
   - inferred_type: use heuristics to detect semantic type:
     - If column name contains "email" or values match email regex → "email"
     - If column name contains "name" and dtype is object → "person_name"
     - If column name contains "phone" or values match phone regex → "phone"
     - If column name contains "date" or dtype is datetime → "date"
     - If column name contains "id" or "ID" → "identifier"
     - If dtype is float/int and values are all positive with 2 decimal places → "monetary"
     - If dtype is object and unique count < 20 → "categorical"
     - If dtype is int/float → "numeric"
     - If dtype is bool or unique count == 2 → "binary"
   - missing_count and missing_pct: count of null/NaN values.
   - unique_count: number of distinct values.
   - For numeric columns: mean, median, std_dev, min_value, max_value.
   - distribution: use scipy.stats.shapiro for normality test. If p > 0.05 → "normal". If skewness > 1 → "right_skewed". If skewness < -1 → "left_skewed". Else → "uniform".
   - outlier_count: use sklearn.ensemble.IsolationForest with contamination=0.05. Count predictions == -1.
   - sample_values: take 5 random non-null values from the column.
   - is_pii and pii_type: set by the tagger engine (not the profiler).
3. Store all results in the column_profiles table.

### ENGINE 3: AUTO-TAGGER (tagger_engine.py)

Purpose: Classify the dataset's domain and detect PII in columns.

Sub-task A — Domain Classification:
1. Concatenate the dataset name + column names into one string. Example: "credit_card_fraud amount time V1 V2 class".
2. Use the HuggingFace pipeline: pipeline("zero-shot-classification", model="facebook/bart-large-mnli").
3. Candidate labels: ["Finance", "Risk", "Marketing", "HR", "Operations", "Compliance", "Products"].
4. Run classification. Take the top label with its confidence score.
5. Store as a tag with tag_category="domain", tag_value=label, confidence=score, method="zero_shot".

Sub-task B — PII Detection:
1. For each column in the dataset, take a sample of 20 non-null values.
2. Check with regex patterns:
   - Email: r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
   - Phone: r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
   - SSN: r'\d{3}-\d{2}-\d{4}'
   - Credit card: r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}'
   If more than 50% of sample values match a regex → flag column as that PII type.
3. For remaining text columns, run spaCy NER on the sample values:
   - Load: nlp = spacy.load("en_core_web_sm")
   - For each value, run doc = nlp(value) and check for entities with label "PERSON".
   - If more than 50% of values contain a PERSON entity → flag as "person_name".
4. Update the column_profiles table: set is_pii=True and pii_type accordingly.
5. If any column has PII, add a dataset-level tag: tag_category="sensitivity", tag_value="contains_pii", method="ner_regex".

### ENGINE 4: QUALITY SCORER (quality_engine.py)

Purpose: Score dataset quality from 0 to 100 across 5 dimensions.

Dimensions and calculation:
1. Completeness (weight 0.30):
   - score = (total_non_null_cells / total_cells) * 100
2. Consistency (weight 0.20):
   - For each column, check if all non-null values have the same format/type.
   - score = (number_of_consistent_columns / total_columns) * 100
   - Consistency checks: are all dates in the same format? Are all numbers the same type? Are categorical values from a consistent set?
3. Uniqueness (weight 0.20):
   - score = (1 - duplicate_rows / total_rows) * 100
4. Validity (weight 0.20):
   - For numeric columns: check if values are within reasonable ranges (e.g., age 0-120, percentages 0-100).
   - For categorical: check if values belong to expected categories.
   - score = (valid_values / total_values) * 100
5. Timeliness (weight 0.10):
   - If the dataset has a date column, check the most recent date.
   - If within last 30 days → 100, within 90 days → 75, within 1 year → 50, older → 25.
   - If no date column, use file modification date.

Overall score = (completeness * 0.30) + (consistency * 0.20) + (uniqueness * 0.20) + (validity * 0.20) + (timeliness * 0.10)

Store all dimension scores and overall score in quality_scores table.
Update the datasets table quality_score field.

### ENGINE 5: DASHBOARD GENERATOR (dashboard_engine.py)

Purpose: Generate a JSON configuration that tells the frontend which charts to render.

Logic:
1. Read the column_profiles for the dataset.
2. Initialize an empty list of charts.
3. Always add: { type: "kpi_cards", data: { rows: row_count, columns: column_count, size: file_size, quality: quality_score } }
4. For each column:
   - If inferred_type is "numeric" or "monetary": add { type: "histogram", column: column_name, data: [values] }
   - If inferred_type is "numeric" or "monetary": add { type: "box_plot", column: column_name, data: { min, q1, median, q3, max, outliers } }
   - If inferred_type is "categorical" and unique_count < 20: add { type: "bar_chart", column: column_name, data: { labels: [...], counts: [...] } }
   - If inferred_type is "categorical" and unique_count < 8: add { type: "pie_chart", column: column_name, data: { labels: [...], values: [...] } }
   - If inferred_type is "binary": add { type: "class_balance", column: column_name, data: { labels: [...], counts: [...] } }
   - If inferred_type is "date": add { type: "time_series", column: column_name, data: { dates: [...], counts: [...] } }
5. If there are 2 or more numeric columns: compute correlation matrix and add { type: "heatmap", data: { columns: [...], matrix: [[...]] } }
6. If any column has missing_pct > 0: add { type: "missing_values_map", data: { columns: [...], missing_pcts: [...] } }
7. Store the full chart config as JSONB in dashboard_configs table.
8. The frontend reads this JSON and renders each chart using the appropriate Recharts component.

---

## INGESTION PIPELINE (pipeline/ingestion.py)

This is the orchestrator. It runs when a user uploads a dataset via POST /api/datasets/upload.

Steps:
1. VALIDATE: Check file extension is .csv, .xlsx, .xls, or .json. Check file size < 500MB. Check encoding is readable.
2. STORE: Save the file to data/datasets/{uuid}_{original_filename}. Create a record in the datasets table with status="processing".
3. PROFILE: Call profiler_engine.profile(dataset_id, file_path). Stores results in column_profiles.
4. TAG: Call tagger_engine.tag(dataset_id, file_path). Stores results in dataset_tags and updates column_profiles for PII.
5. SCORE: Call quality_engine.score(dataset_id). Stores results in quality_scores and updates datasets.quality_score.
6. INDEX: Call search_engine.index(dataset_id). Generates embedding and stores in ChromaDB.
7. DASHBOARD: Call dashboard_engine.generate(dataset_id). Stores config in dashboard_configs.
8. Update datasets table: set status="ready".

If any step fails, set status="error" and log the error.

---

## FRONTEND PAGES

### SearchPage.tsx
- Large search bar at the top (centered, Google-style).
- When user types and submits, call GET /api/search?q={query}.
- Display results as a list of DatasetCard components.
- Each card shows: dataset name, description (first 100 chars), quality score badge, tags, row count, column count, file format.
- Clicking a card navigates to /datasets/{id}.

### BrowsePage.tsx
- Lists all datasets from GET /api/datasets.
- Filter sidebar: filter by domain tag, quality range (slider), file format.
- Sort by: name, quality score, upload date, row count.
- Same DatasetCard components as search results.

### DatasetProfilePage.tsx
- Header: dataset name, format, upload date, quality score badge.
- Tags section: display all tags as colored badges.
- KPI row: row count, column count, file size, quality score.
- Quality breakdown: 5 progress bars (completeness, consistency, uniqueness, validity, timeliness).
- Column table: table with columns — name, inferred type, missing %, unique count, mean, outliers, PII flag.
- Preview button: shows first 50 rows in a data table (from GET /api/datasets/{id}/preview).
- Buttons: "View Dashboard", "Download".

### DashboardPage.tsx
- Fetches dashboard config from GET /api/datasets/{id}/dashboard.
- Reads the JSON config and renders each chart using the matching Recharts component.
- Layout: responsive grid (2 columns on desktop, 1 on mobile).
- KPI cards always at the top.
- Charts rendered dynamically based on the config array.

---

## SYNTHETIC DATA GENERATION (data/synthetic/generate_synthetic.py)

Generate 70-80 synthetic datasets to populate the catalogue. Use Faker + numpy + pandas.

Categories to generate:
- Clients (15 datasets): client profiles, KYC data, segmentation, account info, customer demographics
- Transactions (15 datasets): wire transfers, card payments, ATM withdrawals, online purchases, merchant transactions
- Loans (10 datasets): loan applications, repayment schedules, default records, mortgage data, auto loans
- Risk & Compliance (10 datasets): AML alerts, risk scores, suspicious activity reports, audit logs, compliance checks
- HR (10 datasets): employee records, salary data, branch staff, performance reviews, attendance logs
- Products (10 datasets): account types, credit cards, insurance policies, investment products, savings plans

Each dataset should have:
- Between 500 and 50000 rows (vary the size).
- Between 5 and 25 columns.
- Some datasets should have intentional quality issues: missing values (5-30%), duplicate rows (1-5%), inconsistent formats.
- Some datasets should contain PII columns (names, emails, phones) to test PII detection.
- Save as CSV files in data/synthetic/.

---

## HOW TO RUN THE PROJECT

```bash
# Clone the repository
git clone https://github.com/[owner]/datascout.git
cd datascout

# Start everything with Docker Compose
docker-compose up --build

# The app will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

docker-compose.yml should define 4 services:
- frontend (React, port 3000)
- backend (FastAPI, port 8000)
- db (PostgreSQL, port 5432)
- chromadb (ChromaDB, port 8001)

---

## ENVIRONMENT VARIABLES

```
DATABASE_URL=postgresql://datascout:datascout@db:5432/datascout
CHROMADB_HOST=chromadb
CHROMADB_PORT=8001
UPLOAD_DIR=./data/datasets
MAX_FILE_SIZE_MB=500
```

---

## BUILD ORDER (RECOMMENDED)

If building from scratch, follow this order:

1. Set up Docker Compose with PostgreSQL + ChromaDB containers
2. Create the FastAPI app skeleton with database connection
3. Create the database tables (SQLAlchemy models)
4. Build the profiler engine (most independent, no AI dependencies)
5. Build the quality scorer engine (depends on profiler results)
6. Build the tagger engine (depends on profiler for column data)
7. Build the search engine (depends on tagger for tags in the embedding text)
8. Build the dashboard engine (depends on profiler for chart selection)
9. Build the ingestion pipeline (orchestrates all engines)
10. Build the upload endpoint and dataset CRUD endpoints
11. Build the React frontend: SearchPage → BrowsePage → DatasetProfilePage → DashboardPage
12. Generate synthetic datasets and test the full pipeline
13. Polish UI, handle errors, add loading states