# ─────────────────────────────────────────────────────────────────────────────
# DataScout Frontend - Production Multi-stage Dockerfile
# ─────────────────────────────────────────────────────────────────────────────

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (better layer caching)
COPY package*.json ./

# Use npm cache mount for faster builds
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline

# Copy source files
COPY . .

# Build the application
RUN npm run build

# ─────────────────────────────────────────────────────────────────────────────
# Production stage with Nginx
# ─────────────────────────────────────────────────────────────────────────────
FROM nginx:1.25-alpine AS production

LABEL maintainer="DataScout Team"
LABEL version="1.0.0"
LABEL description="DataScout React frontend with Nginx"

# Install curl for health checks
RUN apk add --no-cache curl

# Remove default nginx config
RUN rm -rf /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 101 -S nginx || true && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx || true

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
