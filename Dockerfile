# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY sqli_system/frontend/package*.json ./
RUN npm install
COPY sqli_system/frontend/ .
RUN npm run build

# Stage 2: Production Backend
FROM python:3.11-slim
WORKDIR /app

# System dependencies for scientific libs
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY sqli_system/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY sqli_system/ /app/sqli_system/

# Copy built frontend assets to a directory served by FastAPI
COPY --from=frontend-builder /app/frontend/dist /app/sqli_system/static

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV MODEL_DIR=/app/sqli_system/saved_models

# Start command
CMD ["uvicorn", "sqli_system.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
