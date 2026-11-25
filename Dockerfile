# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for latam-valuation-engine
# Pattern: builder (compile deps) -> runtime (lean image, install deps fresh)
# Reference: pre-deploy-audit skill, Oct 2026 pension-calc pitfalls

ARG PYTHON_VERSION=3.11
ARG PORT=8000

# ---- Builder stage ----
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# System deps needed to build some wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy source for the package install
COPY pyproject.toml README.md ./
COPY src ./src

# Build a wheel in the builder stage
RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir=/wheels .

# ---- Runtime stage ----
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

# Run as non-root user
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home --shell /bin/bash app

WORKDIR /app

# Runtime system deps (libpq for asyncpg, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install the wheel and ALL its dependencies from scratch. This avoids the
# brittle "copy site-packages from builder" pattern that fails when the
# builder Python minor version differs from the runtime Python minor version.
COPY --from=builder /wheels /wheels
COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --find-links=/wheels "latam-valuation-engine" \
    && rm -rf /wheels

# Copy source (not strictly needed if installed as package, but useful for `python -m`)
COPY src ./src

# Static assets (public, OK to copy)
COPY landing ./landing
COPY data ./data

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

USER app

EXPOSE ${PORT}

# Ensure uvicorn is importable; run as a module so src/ is on PYTHONPATH.
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Uvicorn with workers=1 for memory-constrained free tier.
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers"]
