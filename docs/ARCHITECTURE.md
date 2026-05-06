# DataScout – Architecture Summary

## Overview

DataScout is a full-stack **data discovery and profiling** application. Users can upload datasets, browse/search them, view column profiles and quality scores, and explore auto-generated dashboards with charts.

---

## High-Level Architecture

```
┌─────────────────┐     HTTP/REST      ┌─────────────────┐     ┌──────────────┐
│  React Frontend │ ◄────────────────► │  FastAPI        │ ◄──►│  PostgreSQL  │
│  (Vite, TS)     │   /api/v1/*        │  Backend        │     │  (datasets,  │
└─────────────────┘                    └────────┬────────┘     │   profiles,  │
                                                 │              │   tags, etc) │
                                                 │              └──────────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │  ChromaDB       │
                                        │  (vector store   │
                                        │   for search)    │
                                        └─────────────────┘
```

- **Frontend**: React 19, TypeScript, Vite 7, Tailwind CSS 4, React Router, Recharts.
- **Backend**: FastAPI, async SQLAlchemy, Pydantic.
- **Data**: PostgreSQL (metadata, profiles, tags, quality, dashboard configs), ChromaDB (embeddings for semantic search).
- **Deployment**: Docker Compose with `db`, `chromadb`, `backend`, `frontend` (Nginx) services; backend can use NVIDIA GPU for embedding models.

---

## Project Structure

### Root

- `docker-compose.yml` – Orchestrates db, chromadb, backend, frontend.
- `PHASE4_FRONTEND.md` – Frontend UI rebuild spec (Search, Browse, Profile, Dashboard, Upload).
- `PHASE5_SYNTHETIC_DATA.md` – Spec for synthetic banking data generator.
- `.env.example` – Env template (Postgres, ChromaDB, etc.).

### Backend (`backend/`)

- **Entry**: `main.py` – FastAPI app, CORS, lifespan (upload dir, DB init), mounts `api_router` at `/api/v1`.
- **Config**: `config.py` – Pydantic Settings (DB URL, CORS, upload dir, ChromaDB, etc.).
- **API**: `api/router.py` – Includes dataset routes.  
  `api/routes/datasets.py` – All dataset endpoints: upload, list, get, delete, search, profile, quality, dashboard, preview, tags, reprocess.
- **DB**: `db/database.py` – Async engine/session; `db/models.py` – SQLAlchemy models (Dataset, ColumnProfile, Tag, QualityScore, DashboardConfig).
- **Pipeline**: `pipeline/ingestion.py` – IngestionPipeline: save file, profile, tag, quality, dashboard, index into ChromaDB.
- **Engines**: `engines/` – Profiler, Tagger, Quality, Dashboard, Search (and optional components) used by the pipeline and search route.
- **Scripts**: `scripts/generate_synthetic_data.py` – Generates synthetic banking CSVs and `manifest.json` under `data/synthetic/`.

### Frontend (`frontend/`)

- **Entry**: `src/main.tsx` → `App.tsx` – Routes: `/` (SearchPage), `/browse` (BrowsePage), `/datasets/:id` (DatasetProfilePage), `/datasets/:id/dashboard` (DashboardPage). Global Upload modal.
- **Services**: `src/services/api.ts` – Fetch-based client for all backend endpoints (list, get, delete, reprocess, upload, profile, quality, dashboard, preview, tags, search, getGlobalStats).
- **Types**: `src/types/dataset.ts` – Shared TypeScript types (Dataset, DatasetDetail, ColumnProfile, Tag, QualityScoreDetail, DashboardConfig, ChartConfig, SearchResult, DataPreview, etc.).
- **Pages**: Search (hero, search bar, KPIs, recent datasets), Browse (filters, grid, pagination), DatasetProfile (header, KPIs, tabs: columns/preview/quality, dashboard link), Dashboard (charts grid from config).
- **Components**: Common (Navbar, SearchBar, KPICard, QualityBadge, TagBadge, LoadingSpinner, SkeletonCard), dataset (DatasetCard, DatasetCardExpanded, DatasetHeader, QualityBreakdown, ColumnProfileTable, DataPreviewTable), charts (Histogram, Pie, BoxPlot, Heatmap, MissingValuesMap), filters (FilterSidebar, Domain, Quality, Format, PII), upload (UploadModal, DropZone, ProgressSteps, SuccessSummary).

### Data

- `data/synthetic/` – Generated CSVs and `manifest.json` (PHASE5 output); used for testing and demos.

---

## Key Data Flows

1. **Upload**: User selects file in UploadModal → `POST /api/v1/datasets/upload` → backend saves file, creates Dataset row, runs IngestionPipeline in background (profile, tag, quality, dashboard, ChromaDB index). Frontend shows progress steps then success.
2. **Browse**: `GET /api/v1/datasets` with filters/pagination → list of datasets; optional client-side quality filter. Frontend shows loading state, then grid.
3. **Profile**: `GET /api/v1/datasets/:id`, `.../profile`, `.../preview` (and optionally quality) → DatasetDetail, column profiles, preview rows. Rendered in tabs with loading spinner.
4. **Dashboard**: `GET /api/v1/datasets/:id/dashboard` → chart configs; frontend maps chart types to Recharts components (histogram, pie, box, heatmap, missing).
5. **Search**: `GET /api/v1/datasets/search?q=...` → semantic search via ChromaDB; results show relevance and matched columns.

---

## Technology Summary

| Layer    | Tech |
|----------|------|
| Frontend | React 19, TypeScript, Vite 7, Tailwind CSS 4, React Router 7, Recharts |
| Backend  | FastAPI, Pydantic, SQLAlchemy (async), Pandas |
| Database | PostgreSQL 15, ChromaDB (vector) |
| DevOps   | Docker Compose, Nginx (frontend), optional NVIDIA runtime (backend) |

---

## Notes

- Backend uses async throughout; pipeline and search depend on ChromaDB and optional GPU for embeddings.
- Frontend uses a single `api.ts` with typed requests; loading and error states are handled per page/modal.
- PHASE4 defines the current UI (pages and components). PHASE5 defines the synthetic data script and output layout.
