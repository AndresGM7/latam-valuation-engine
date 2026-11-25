# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for latam-valuation-engine
# Pattern: builder -> runtime (lean image, no dev deps)
# Reference: pre-deploy-audit skill, Oct 2026 pension-calc pitfalls

ARG PYTHON_VERSION=3.11
ARG PORT=8000

# ---- Builder stage ----
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# System deps needed to build some wheels (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY what's needed for dependency resolution first (cache layer)
COPY pyproject.toml README.md ./
COPY src ./src

# Install deps. We DON'T install dev extras in the production image.
# Devs run `pip install -e .[dev,data]` locally.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# ---- Runtime stage ----
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

# Run as non-root user
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home --shell /bin/bash app

WORKDIR /app

# Runtime system deps (just libpq for asyncpg, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Discover the actual Python version directory at build time.
# PYTHON_VERSION may be "3.11" while the actual dir is "python3.11" or "python3.11.18".
# We use a wildcard to match either form, which is portable across python:3.11 images.
COPY --from=builder /usr/local/lib/python3*/site-packages /usr/local/lib/python3*/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /build/src ./src

# Static assets (landing, docs) — these are public, OK to copy
COPY landing ./landing
COPY data ./data

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

USER app

EXPOSE ${PORT}

# Uvicorn with workers=1 for memory-constrained free tier.
# Scale with `fly scale count` for more concurrency.
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers"]
