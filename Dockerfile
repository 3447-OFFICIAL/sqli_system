# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend-simple/package*.json ./
RUN npm install
COPY frontend-simple/ .
RUN npm run build

# Stage 2: Production Backend
FROM python:3.11-slim
WORKDIR /app

# System dependencies for scientific libs
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app/

# Copy built frontend assets to a directory served by FastAPI
# Create static dir if it doesn't exist
RUN mkdir -p /app/static
COPY --from=frontend-builder /app/frontend/dist /app/static

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV MODEL_DIR=/app/saved_models

# Start command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
