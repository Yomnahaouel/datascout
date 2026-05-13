# Start DataScout in fast development mode.
# Normal code changes do not need docker compose up --build.

$ErrorActionPreference = "Stop"

docker compose -f docker-compose.yml -f docker-compose.dev.yml up
