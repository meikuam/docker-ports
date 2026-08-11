from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services import list_containers_data, get_stats_data, get_docker_client

app = FastAPI(title="Docker Ports Viewer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - main admin page"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception:
        raise HTTPException(status_code=500, detail="Template rendering failed")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = get_docker_client()
        client.ping()
        return {"status": "healthy", "docker": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Health check failed")


@app.get("/containers")
async def list_containers():
    """List all containers with their port bindings"""
    try:
        return {"containers": list_containers_data()}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/stats")
async def get_stats():
    """Get CPU/Memory statistics from containers"""
    try:
        return {"stats": get_stats_data()}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)