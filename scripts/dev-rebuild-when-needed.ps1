# Slow command: use ONLY when dependencies changed.
# Examples: backend/requirements.txt, frontend/package.json, Dockerfile, docker-compose*.yml.

docker compose -f docker-compose.dev.yml up --build
