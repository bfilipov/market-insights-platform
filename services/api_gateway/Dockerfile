# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install Poetry without creating a virtual environment inside Docker
RUN pip install --no-cache-dir poetry==1.8.3

# Copy only dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install dependencies to the system python
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi --no-root

# ==========================================
# Stage 2: Runner
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY api_gateway/ ./api_gateway/

# Create a non-root user for security
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Run using the module path
CMD ["python", "-m", "api_gateway.main"]