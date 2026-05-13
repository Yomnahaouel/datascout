# Danger: resets PostgreSQL and ChromaDB data volumes.
# Use only when you want a completely fresh local database.

$ErrorActionPreference = "Stop"

Write-Host "This will delete local DataScout database/vector data." -ForegroundColor Yellow
$confirm = Read-Host "Type RESET to continue"
if ($confirm -ne "RESET") {
  Write-Host "Cancelled."
  exit 0
}

docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
