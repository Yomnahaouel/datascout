# Restart only backend without rebuilding images.
# Use this when backend did not auto-reload or after changing env/config.

docker compose -f docker-compose.dev.yml restart backend
