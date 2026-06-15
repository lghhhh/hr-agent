# ===== Build Frontend =====
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ===== Backend =====
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create data directory
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
