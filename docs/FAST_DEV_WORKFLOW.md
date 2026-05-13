# Fast Dev Workflow

This workflow avoids slow `docker compose up --build` runs after every `git pull` or small code change.

## Daily command

On Windows PowerShell:

```powershell
.\scripts\dev-up.ps1
```

Equivalent manual command:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Open:

- Frontend: <http://localhost:3000>
- Backend: <http://localhost:8000/health>
- API docs: <http://localhost:8000/docs>

## Why this is faster

`docker-compose.dev.yml` mounts local source code into the containers:

- `./backend:/app` for FastAPI with `uvicorn --reload`
- `./frontend:/app` for Vite dev server
- persistent `frontend_node_modules`, `npm_cache`, `pip_cache`, and `model_cache` volumes

So normal edits to `.py`, `.tsx`, `.ts`, `.css`, docs, etc. do **not** need an image rebuild.

## After `git pull`

Usually run only:

```powershell
.\scripts\dev-up.ps1
```

Use rebuild only when dependencies or Docker files changed.

## When rebuild is needed

Run:

```powershell
.\scripts\dev-rebuild-when-needed.ps1
```

Only if one of these changed:

- `backend/requirements.txt`
- `frontend/package.json`
- `frontend/package-lock.json`
- `backend/Dockerfile` or `backend/Dockerfile.cpu`
- `frontend/Dockerfile`
- `docker-compose.yml` or `docker-compose.dev.yml`

## Stop without deleting data

```powershell
.\scripts\dev-down.ps1
```

## Reset database/vector data

Danger: this deletes local PostgreSQL and ChromaDB data.

```powershell
.\scripts\dev-reset-data.ps1
```

Use this only when stale uploaded datasets or old database state cause confusing results.
