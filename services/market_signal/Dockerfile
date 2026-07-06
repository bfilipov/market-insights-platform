FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir poetry==2.4.1
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY market_signal/ ./market_signal/

RUN useradd --create-home appuser
USER appuser

EXPOSE 8002
CMD ["python", "-m", "market_signal.main"]