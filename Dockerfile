FROM python:3.12-slim-bullseye

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set workdir and copy dependency files
WORKDIR /app
COPY pyproject.toml uv.lock ./


# Install the application dependencies and uvicorn
RUN uv sync --frozen --no-cache \
    && /bin/uv pip install uvicorn

# Copy the application code
COPY ./src /app

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the application using uvicorn
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]