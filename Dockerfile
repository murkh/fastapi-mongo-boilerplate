# syntax=docker/dockerfile:1

# --- Builder stage ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Install pipenv for dependency management (optional, but here we use pip only)

# Copy only requirements to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install pip-tools to compile requirements (if using pip-tools)
RUN pip install --upgrade pip && pip install uv

# Install dependencies in a virtual environment
RUN uv pip install --system --no-cache-dir .

# --- Final stage ---
FROM python:3.12-slim

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src ./src
COPY pyproject.toml uv.lock ./

# Expose port for uvicorn
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Command to run the app
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
