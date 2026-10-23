# ==============================================================================
# StayNearby Multi-Stage Production Dockerfile for Render / Cloud Deployments
# ==============================================================================

# --- Stage 1: Frontend Build ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python Backend Runtime ---
FROM python:3.12-slim AS runner
WORKDIR /app

# Install system dependencies (libpq for postgresql)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code, migrations, and ML artifacts
COPY backend ./backend
COPY alembic.ini ./alembic.ini
COPY .env.example ./.env

# Copy compiled frontend from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Initialize database, seed demonstration data, and train models
RUN alembic upgrade head && \
    python -m backend.scripts.seed_data && \
    python -m backend.app.ml.train_recommender && \
    python -m backend.app.ml.train_demand_model

ENV PORT=8000
ENV ENVIRONMENT=production

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
