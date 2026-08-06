from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import docker
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Docker Ports Viewer", version="1.0.0")

async def get_docker_client():
    """Create and return Docker client"""
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        logger.error(f"Docker connection failed: {e}")
        raise HTTPException(status_code=503, detail="Cannot connect to Docker daemon")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Docker Ports Viewer API",
        "endpoints": {
            "/containers": "List all containers and their ports",
            "/containers/{container_id}": "Get details of specific container",
            "/health": "Health check endpoint"
        }
    }

@app.get("/containers")
async def list_containers():
    """List all containers with their port bindings"""
    client = await get_docker_client()
    
    try:
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
            
            for port_binding in container.attrs.get('NetworkSettings', {}).get('Ports', {}):
                container_info["ports"].append({
                    "container_port": port_binding,
                    "host_bindings": list(port_binding.values()) if port_binding else []
                })
            
            containers_data.append(container_info)
        
        return {"containers": containers_data}
    
    except Exception as e:
        logger.error(f"Error listing containers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/containers/{container_id}")
async def get_container(container_id: str):
    """Get details of specific container"""
    client = await get_docker_client()
    
    try:
        container = client.containers.get(container_id)
        
        if container is None:
            raise HTTPException(status_code=404, detail="Container not found")
        
        container_attrs = container.attrs
        
        return {
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags[0] if container.image.tags else None,
            "ports": list(container_attrs['NetworkSettings']['Ports'].keys()) if container_attrs.get('NetworkSettings', {}).get('Ports') else [],
            "created": container_attrs.get('Created', ''),
            "state": container_attrs.get('State', {}),
            "ip_address": container_attrs.get('NetworkSettings', {}).get('IPAddress', 'Not assigned'),
            "mac_address": container_attrs.get('NetworkSettings', {}).get('MacAddress', 'Not assigned')
        }
    
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except Exception as e:
        logger.error(f"Error getting container details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = await get_docker_client()
        client.ping()
        return {"status": "healthy", "docker": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unavailable: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)