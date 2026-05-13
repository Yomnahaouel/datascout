# DataScout

DataScout is an AI-powered smart data catalogue for banking datasets. It helps upload datasets, profile columns, detect missing values, detect sensitive/PII fields, classify business domains, calculate data quality scores, and generate dashboards.

## Main Features

- Upload CSV / Excel datasets.
- Automatic column profiling: type, missing values, uniqueness, examples.
- PII detection: email, phone number, credit card number, SSN, person names when detectable.
- Domain tagging: Finance, Risk, Marketing, HR, Operations, Compliance, Products.
- Data quality scoring.
- Dashboard generation support, disabled by default for faster local uploads.
- Semantic/vector search support through ChromaDB, disabled by default for faster local uploads.

## Tech Stack

- **Frontend:** React + Vite + TypeScript + Nginx
- **Backend:** FastAPI + Python
- **Database:** PostgreSQL
- **Vector database:** ChromaDB
- **Containerization:** Docker Compose

## Prerequisites

Before running the project locally, install:

1. **Git**
2. **Docker Desktop**
3. **VS Code** or any code editor

Make sure Docker Desktop is open and running before starting the project.

Check installation:

```bash
docker --version
docker compose version
git --version
```

## Project Setup Locally

### 1. Clone the repository

```bash
git clone https://github.com/Yomnahaouel/datascout.git
cd datascout
```

### 2. Create the environment file

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell, if `cp` does not work:

```powershell
Copy-Item .env.example .env
```

Recommended local `.env` content:

```env
POSTGRES_USER=datascout
POSTGRES_PASSWORD=datascout
POSTGRES_DB=datascout
CHROMA_AUTH_TOKEN=datascout
CUDA_VISIBLE_DEVICES=0
DEBUG=false

# Fast local demo defaults: avoid heavy model downloads during uploads.
DATASCOUT_HEAVY_ML=false
DATASCOUT_SEMANTIC_SEARCH=false
DATASCOUT_GENERATE_DASHBOARD=false
```

Keep these three `DATASCOUT_*` flags as `false` for a smooth local demo. Set them to `true` only when you explicitly want the heavier BART domain classifier, semantic/vector indexing, or generated dashboard configs.

Important: if the PostgreSQL volume already exists from an older run, keep the same `POSTGRES_PASSWORD` that was used when the database was first created. If the backend cannot connect to the database, see the troubleshooting section below.

### 3. Start the project

For the first run:

```bash
docker compose up --build
```

This can take time because Docker has to download and build all services.

For normal next runs, use:

```bash
docker compose up
```

Do **not** use `--build` every time unless dependencies or Docker files changed.

### Fast development mode

For faster work after code changes or `git pull`, use the dev override:

```powershell
.\scripts\dev-up.ps1
```

Equivalent manual command:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This mounts backend/frontend source files into the containers, so normal `.py`, `.tsx`, `.ts`, `.css`, and documentation changes do not need a full rebuild.

Full guide: `docs/FAST_DEV_WORKFLOW.md`.

### 4. Open the application

After all containers are healthy, open:

- Frontend: <http://localhost:3000>
- Backend health check: <http://localhost:8000/health>
- Backend API docs: <http://localhost:8000/docs>
- ChromaDB: <http://localhost:8001>

Expected backend health response:

```json
{"status": "ok"}
```

## Docker Services

The project starts 4 main containers:

| Service | Container | Port | Role |
|---|---|---:|---|
| PostgreSQL | `datascout-db` | `5432` | Main relational database |
| ChromaDB | `datascout-chromadb` | `8001` | Vector database |
| Backend | `datascout-backend` | `8000` | FastAPI API |
| Frontend | `datascout-frontend` | `3000` | React/Nginx web app |

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs backend --tail=100
```

Stop the project:

```bash
docker compose down
```

Stop and delete volumes/database data only if you really want a fresh database:

```bash
docker compose down -v
```

Warning: `docker compose down -v` deletes PostgreSQL and ChromaDB stored data.

## How to Test the Project

### 1. Upload a dataset

1. Open <http://localhost:3000>
2. Click **Importer / Upload**
3. Select a CSV or Excel file
4. Wait until the dataset status is completed
5. Open the dataset details page

### 2. Verify dataset profiling

For each uploaded dataset, check:

- Total rows
- Number of columns
- Quality score
- Missing values per column
- Column type detection
- PII fields count
- Domain/category tags
- Data preview
- Dashboard page

### 3. Recommended test order

Use small or medium files first.

Recommended datasets:

1. A clean dataset without PII
2. A dataset with missing values
3. A banking/finance dataset
4. A risk/fraud/credit dataset
5. A dataset containing fake PII values for testing

Public datasets often remove real PII, so `PII Fields = 0` can be normal for real datasets.

## Testing PII Detection

To test PII detection correctly, use a controlled synthetic CSV containing fake personal data. Example:

```csv
customer_id,full_name,email,phone,credit_card_number,account_balance,city
C001,John Smith,john.smith@gmail.com,+216 55 123 456,4539 1488 0343 6467,1200,Tunis
C002,Sarah Johnson,sarah.johnson@yahoo.com,+216 22 987 654,6011 1111 1111 1117,3500,Sousse
C003,Michael Brown,michael.brown@hotmail.com,+216 99 111 222,5555 5555 5555 4444,,Sfax
C004,Emma Wilson,emma.wilson@gmail.com,+216 20 333 444,4111 1111 1111 1111,900,Tunis
C005,David Miller,david.miller@outlook.com,+216 58 777 888,3782 822463 10005,,Nabeul
```

Expected result:

- `full_name` detected as person/name when NER recognizes it
- `email` detected as email
- `phone` detected as phone number
- `credit_card_number` detected as credit card
- `account_balance` has missing values

## Generate Synthetic Data

If needed, generate project synthetic datasets inside the backend container:

```bash
docker compose exec backend python scripts/generate_synthetic_data.py
```

Generated files are stored under:

```text
data/synthetic
```

Check generated files:

```bash
ls data/synthetic
```

On Windows PowerShell:

```powershell
dir data\synthetic
```

## Useful API Commands

List datasets:

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/datasets" | ConvertTo-Json -Depth 5
```

Get one dataset by ID:

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/datasets/DATASET_ID" | ConvertTo-Json -Depth 10
```

Get dataset tags:

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/datasets/DATASET_ID/tags" | ConvertTo-Json -Depth 10
```

Backend logs:

```powershell
docker compose logs backend --tail=120
```

## When to Rebuild Docker

In fast dev mode, use:

```powershell
.\scripts\dev-rebuild-when-needed.ps1
```

For the normal production-like stack, use:

```bash
docker compose up --build
```

only when one of these files changed:

- `backend/requirements.txt`
- `frontend/package.json`
- `frontend/package-lock.json`
- `backend/Dockerfile`
- `backend/Dockerfile.cpu`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `docker-compose.dev.yml`

For normal restart, use:

```bash
docker compose up
```

or, for fast dev mode:

```powershell
.\scripts\dev-up.ps1
```

## Troubleshooting

### Backend is unhealthy or fails to start

Check logs:

```bash
docker compose logs backend --tail=120
```

### Error: `No address associated with hostname`

If logs show something like:

```text
socket.gaierror: [Errno -5] No address associated with hostname
```

check the database URL:

```powershell
docker compose config | Select-String "DATABASE_URL"
```

Expected format:

```text
DATABASE_URL: postgresql://datascout:datascout@db:5432/datascout
```

The hostname must be `db`, not `localhost`.

### PostgreSQL password problem

If the database volume was created with an old password, changing `.env` later may break backend connection.

Options:

1. Put the old password back in `.env`
2. Or reset the database completely:

```bash
docker compose down -v
docker compose up --build
```

Warning: this deletes local database data.

### Frontend opens but API calls fail

Check that backend is healthy:

```bash
curl http://localhost:8000/health
```

On PowerShell:

```powershell
Invoke-RestMethod "http://localhost:8000/health"
```

Also check backend logs:

```bash
docker compose logs backend --tail=120
```

## Project Structure

```text
datascout/
├── backend/              # FastAPI backend
├── frontend/             # React/Vite frontend
├── data/                 # Local datasets and generated synthetic data
├── docs/                 # Project documentation and schemas
├── docker-compose.yml    # Local Docker Compose stack
├── .env.example          # Example environment variables
└── README.md             # Local setup guide
```

## Notes for Collaborators

- Always start Docker Desktop before running the project.
- First build can take several minutes.
- Use `docker compose up` for normal runs.
- Use `docker compose up --build` only when dependencies or Docker files changed.
- Public datasets usually do not contain real PII.
- For PII tests, use fake/synthetic emails, phone numbers, names, credit card numbers, and SSNs.
- If a dataset fails, check `docker compose logs backend --tail=120` before changing code.
