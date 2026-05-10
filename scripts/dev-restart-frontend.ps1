# Restart only frontend without rebuilding images.
# Use this when Vite did not auto-refresh.

docker compose -f docker-compose.dev.yml restart frontend
