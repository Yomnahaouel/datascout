# ─────────────────────────────────────────────────────────────────────────────
# DataScout Backend - Production Dockerfile with NVIDIA GPU Support
# ─────────────────────────────────────────────────────────────────────────────

# Build stage for compiling dependencies
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install Python dependencies with pip cache mount
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Production stage
# ─────────────────────────────────────────────────────────────────────────────
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04 AS production

LABEL maintainer="DataScout Team"
LABEL version="1.0.0"
LABEL description="DataScout FastAPI backend with GPU support"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Create non-root user for security
RUN groupadd -r datascout && useradd -r -g datascout datascout

# Create necessary directories
RUN mkdir -p /app/data/datasets /cache/huggingface && \
    chown -R datascout:datascout /app /cache

# Copy application code
COPY --chown=datascout:datascout . .

# Environment variables for HuggingFace cache
ENV HF_HOME=/cache/huggingface
ENV TRANSFORMERS_CACHE=/cache/huggingface/transformers
ENV SENTENCE_TRANSFORMERS_HOME=/cache/huggingface/sentence_transformers

# Switch to non-root user
USER datascout

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
