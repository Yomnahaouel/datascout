# Stop DataScout dev containers without deleting database/vector volumes.

$ErrorActionPreference = "Stop"

docker compose -f docker-compose.yml -f docker-compose.dev.yml down
