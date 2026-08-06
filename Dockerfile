FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install --upgrade pip && pip install --no-cache-dir poetry && poetry install --no-root --no-dev

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["gunicorn", "main:app", "--workers", "2", "--bind", "0.0.0.0:8000", "--access-logfile", "-"]