# Use this only when dependencies or Docker files changed:
# - backend/requirements.txt
# - frontend/package.json or package-lock.json
# - backend/Dockerfile* / frontend/Dockerfile
# - docker-compose.yml / docker-compose.dev.yml

$ErrorActionPreference = "Stop"

docker compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache backend
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
