# DataScout fast development startup for Windows PowerShell
# Usage from project root: .\scripts\dev-up.ps1

Write-Host "Starting DataScout in fast DEV mode..." -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Docs:     http://localhost:8000/docs" -ForegroundColor Green

# No --build here on purpose. Code changes are mounted live with Docker volumes.
docker compose -f docker-compose.dev.yml up
