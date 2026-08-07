FROM python:3.13-slim

WORKDIR /app

RUN pip install --upgrade pip

# Install dependencies using Poetry
COPY pyproject.toml ./
COPY poetry.lock ./
RUN pip install --no-cache-dir poetry-core && \
    poetry lock --no-update && \
    poetry install --no-interaction --no-root --no-ansi

# Copy application
COPY --chown=app . .

# Create non-root user
RUN useradd -m -u 1001 app && \
    chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["gunicorn", "main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "1", "--bind", "0.0.0.0:8000"]