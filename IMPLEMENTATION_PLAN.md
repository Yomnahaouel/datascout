# DataScout Implementation Plan
## AI-Powered Smart Data Catalogue for Banking

**Lead:** 7afnawi (AI)
**Developer:** GitHub Copilot (via Agent Mode)
**Reviewer:** Hefny
**Date:** 2026-03-06

---

## 📊 Current Status Assessment

### What Exists (Skeleton Only)
- ✅ Backend folder structure (empty implementations)
- ✅ Frontend folder structure (basic React scaffold)
- ❌ No actual AI/ML engines
- ❌ No database connections
- ❌ No real functionality
- ❌ UI is basic/ugly (1/10 rating)

---

## 🎯 Phase 1: Infrastructure (Docker + GPU)

### 1.1 Docker Compose with GPU Support
- [ ] PostgreSQL 15 with persistent volume
- [ ] ChromaDB for vector storage
- [ ] FastAPI backend with GPU access
- [ ] React frontend (production build)
- [ ] Shared volumes for pip/npm caches

### 1.2 Volume Strategy
```yaml
volumes:
  postgres_data:      # Database persistence
  chroma_data:        # Vector DB persistence  
  pip_cache:          # Python packages (download once)
  npm_cache:          # Node packages (download once)
  model_cache:        # AI models (HuggingFace cache)
  upload_data:        # Uploaded datasets
```

---

## 🎯 Phase 2: Backend - Core AI Engines

### 2.1 Profiler Engine (`engines/profiler_engine.py`)
- [ ] Column type detection (numeric, categorical, date, text)
- [ ] Statistical analysis (mean, median, std, distribution)
- [ ] Missing value analysis
- [ ] Outlier detection (IsolationForest)
- [ ] Sample value extraction

### 2.2 Tagger Engine (`engines/tagger_engine.py`)
- [ ] Domain classification (BART zero-shot) - **GPU**
- [ ] PII detection with regex (email, phone, SSN, credit card)
- [ ] PII detection with spaCy NER (names) - **GPU optional**
- [ ] Sensitivity tagging

### 2.3 Quality Engine (`engines/quality_engine.py`)
- [ ] Completeness score (null analysis)
- [ ] Consistency score (format checks)
- [ ] Uniqueness score (duplicate detection)
- [ ] Validity score (range/format validation)
- [ ] Timeliness score (date freshness)
- [ ] Overall weighted score (0-100)

### 2.4 Search Engine (`engines/search_engine.py`)
- [ ] Sentence-transformers embedding (all-MiniLM-L6-v2) - **GPU**
- [ ] ChromaDB vector storage
- [ ] Semantic search with cosine similarity
- [ ] Result ranking

### 2.5 Dashboard Engine (`engines/dashboard_engine.py`)
- [ ] Auto chart selection based on data types
- [ ] Histogram for numeric columns
- [ ] Bar/Pie charts for categorical
- [ ] Time series for date columns
- [ ] Correlation heatmap
- [ ] Missing values visualization

---

## 🎯 Phase 3: Backend - API & Database

### 3.1 Database Models (SQLAlchemy)
- [ ] datasets table
- [ ] column_profiles table
- [ ] dataset_tags table
- [ ] quality_scores table
- [ ] dashboard_configs table

### 3.2 API Endpoints
- [ ] POST /api/datasets/upload - File upload + processing
- [ ] GET /api/datasets - List with filters
- [ ] GET /api/datasets/{id} - Full details
- [ ] DELETE /api/datasets/{id}
- [ ] GET /api/datasets/{id}/preview
- [ ] GET /api/search?q={query}
- [ ] GET /api/datasets/{id}/profile
- [ ] GET /api/datasets/{id}/tags
- [ ] GET /api/datasets/{id}/quality
- [ ] GET /api/datasets/{id}/dashboard

### 3.3 Ingestion Pipeline
- [ ] File validation
- [ ] Async processing
- [ ] Profile → Tag → Score → Index → Dashboard
- [ ] Status updates

---

## 🎯 Phase 4: Frontend - Beautiful UI

### 4.1 Design System
- [ ] Color palette (banking/professional)
- [ ] Typography
- [ ] Component library (cards, badges, buttons)
- [ ] Responsive layout

### 4.2 Pages (Complete Redesign)
- [ ] **SearchPage** - Google-style search, result cards
- [ ] **BrowsePage** - Grid/List view, filters sidebar, sorting
- [ ] **DatasetProfilePage** - Hero section, quality gauge, column table, preview
- [ ] **DashboardPage** - Dynamic chart grid, KPI cards

### 4.3 Components
- [ ] SearchBar with suggestions
- [ ] DatasetCard (thumbnail, quality badge, tags)
- [ ] QualityGauge (circular progress)
- [ ] TagBadge (colored by type)
- [ ] ProfileTable (sortable, filterable)
- [ ] Chart components (Histogram, Bar, Pie, Heatmap, TimeSeries)
- [ ] FileUpload with drag-drop
- [ ] LoadingStates and Skeletons

---

## 🎯 Phase 5: Synthetic Data & Testing

### 5.1 Generate 70-80 Datasets
- [ ] Clients (15 datasets)
- [ ] Transactions (15 datasets)
- [ ] Loans (10 datasets)
- [ ] Risk/Compliance (10 datasets)
- [ ] HR (10 datasets)
- [ ] Products (10 datasets)

### 5.2 Quality Variations
- [ ] Some with missing data (5-30%)
- [ ] Some with duplicates
- [ ] Some with PII
- [ ] Various sizes (500 - 50,000 rows)

---

## 📋 Execution Order

1. **TODAY - Phase 1**: Docker setup with GPU + volumes
2. **Phase 2**: Implement AI engines one by one
3. **Phase 3**: Database + API endpoints
4. **Phase 4**: Beautiful frontend redesign
5. **Phase 5**: Generate test data, full testing

---

## 🤖 Copilot Collaboration Strategy

For each task:
1. Open VS Code with `Ctrl+Shift+Alt+I` (Agent mode)
2. Give detailed prompt with context
3. Monitor progress, approve commands
4. Review generated code
5. Test functionality
6. Iterate if needed

---

## Let's Start!

**First Task:** Create Docker infrastructure with GPU support and volume caching.
