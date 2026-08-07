# Development and deployment

## Running

**Local (no Docker):**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Docker:**
```bash
# Create .env with DOCKER_TLS_VERIFY=0 if your Docker daemon uses TLS
echo "DOCKER_TLS_VERIFY=0" > .env
docker compose up -d
```

The app requires Docker socket access (for inspecting containers) via `/var/run/docker.sock` mounted as read-only.


**requirements**

project requirements are set in poetry with pyproject.toml file



## Build

```bash
docker build -t docker-ports-viewer .
```

## Tests

No tests exist yet. Add pytest + httpx for API tests (`/health`, `/containers`, `/stats`).

## Lint

```bash
python -m ruff check .
# or fix auto-fixable issues
python -m ruff check --fix .
```

## API endpoints

- `GET /` - HTML main page (Jinja2 template)
- `GET /health` - Docker socket health check
- `GET /containers` - List containers + port bindings
- `GET /stats` - CPU/Memory/network stats for all containers

## TLS handling

If your Docker daemon uses TLS, set `DOCKER_TLS_VERIFY=0` in `.env` to disable TLS for the Docker Python client. This is required when accessing a non-TLS Docker socket.
