from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import docker
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Docker Ports Viewer", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - main admin page"""
    try:
        with open("/app/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Template file not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = docker.from_env()
        client.ping()
        return {"status": "healthy", "docker": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/containers")
async def list_containers():
    """List all containers with their port bindings"""
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        containers_data = []
        
        for container in containers:
            container_info = {
                "id": container.id[:12],
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else container.image.id[:12],
                "ports": []
            }
            
            ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
            if isinstance(ports, dict):
                for container_port, host_bindings in ports.items():
                    if isinstance(host_bindings, list):
                        bindings = []
                        for binding in host_bindings:
                            if binding and isinstance(binding, dict):
                                host_port = binding.get('HostPort')
                                ip_address = binding.get('HostIp', '0.0.0.0')
                                bindings.append(f"{ip_address}:{host_port}" if host_port else ip_address)
                        container_info["ports"].append({
                            "container_port": container_port,
                            "host_bindings": bindings
                        })
            
            containers_data.append(container_info)
        
        return {"containers": containers_data}
    
    except Exception as e:
        logger.error(f"Error listing containers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
