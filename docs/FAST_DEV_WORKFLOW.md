# DataScout — Fast development workflow

Use this workflow when you modify DataScout often and do not want to wait for `docker compose --build` every time.

## Daily start

From the project root:

```powershell
.\scripts\dev-up.ps1
```

Or manually:

```powershell
docker compose -f docker-compose.dev.yml up
```

Open:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- Backend API docs: `http://localhost:8000/docs`

## When you change frontend code

Files in `frontend/src` are mounted into the container. Vite hot reload should refresh automatically.

If it does not refresh:

```powershell
.\scripts\dev-restart-frontend.ps1
```

## When you change backend code

Files in `backend` are mounted into the container. FastAPI/Uvicorn `--reload` should restart automatically.

If it does not restart:

```powershell
.\scripts\dev-restart-backend.ps1
```

## When you MUST rebuild

Use rebuild only after changing dependencies or Docker setup:

- `backend/requirements.txt`
- `frontend/package.json`
- `frontend/package-lock.json`
- `backend/Dockerfile*`
- `frontend/Dockerfile`
- `docker-compose*.yml`

Command:

```powershell
.\scripts\dev-rebuild-when-needed.ps1
```

## Important rule

For normal Python/React code changes, do **not** use:

```powershell
docker compose --build
```

Use the dev stack instead:

```powershell
docker compose -f docker-compose.dev.yml up
```

This is faster because:

- backend source code is mounted with `./backend:/app`
- frontend source code is mounted with `./frontend:/app`
- backend uses `uvicorn --reload`
- frontend uses Vite hot reload
- pip/npm/model caches are stored in Docker volumes
