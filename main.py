from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import docker
import logging

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.title or "Docker Ports Viewer",
    version=settings.version or "1.0.0"
)

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
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise HTTPException(status_code=500, detail="Template rendering failed")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = docker.from_env()
        client.ping()
        return {"status": "healthy", "docker": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
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
                "ports": []
            }

            image = None
            try:
                image = container.image.tags[0] if container.image and container.image.tags else None
            except (AttributeError, IndexError, TypeError):
                try:
                    image = container.image.id[:12]
                except AttributeError:
                    image = "unknown"

            if image:
                container_info["image"] = image

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


@app.get("/stats")
async def get_stats():
    """Get CPU/Memory statistics from containers"""
    try:
        client = docker.from_env()

        def get_stats_for_container(container):
            try:
                stats = container.stats(stream=False)

                logger.debug(f"Stats for {container.name}: {list(stats.keys())}")

                cpu_percent = 0
                cpu_stats = stats.get('cpu_stats', {})
                precpu_stats = stats.get('precpu_stats', {})

                if cpu_stats and 'cpu_usage' in cpu_stats:
                    cpu_usage = cpu_stats['cpu_usage']
                    percpu_usage = cpu_stats.get('percpu_usage', [])

                    logger.debug(f"CPU usage: total={cpu_usage.get('total_usage')}, percpu={len(percpu_usage)}")

                    if precpu_stats and 'cpu_usage' in precpu_stats:
                        precpu_usage = precpu_stats['cpu_usage']
                        precpu_percpu_usage = precpu_stats.get('percpu_usage', [])

                        logger.debug(f"PreCPU usage: total={precpu_usage.get('total_usage')}, percpu={len(precpu_percpu_usage)}")

                        if 'total_usage' in cpu_usage and 'total_usage' in precpu_usage:
                            percpu_delta = sum(precpu_percpu_usage) - sum(percpu_usage)

                            system_delta = cpu_usage.get('system_cpu_usage', 0) - precpu_usage.get('system_cpu_usage', cpu_usage.get('system_cpu_usage', 0))

                            logger.debug(f"System delta: {system_delta}, percpu_delta: {percpu_delta}")

                            if system_delta > 0:
                                cpu_percent = (percpu_delta / system_delta) * 100
                            else:
                                cpu_percent = percpu_delta if percpu_delta > 0 else 0
                                logger.debug(f"CPU calc fallback: {cpu_percent}")

                memory_percent = 0
                memory_stats = stats.get('memory_stats', {})
                if 'limit' in memory_stats and memory_stats['limit'] > 0:
                    memory_percent = memory_stats.get('usage', 0) / memory_stats['limit'] * 100

                net_input = 0
                net_output = 0
                networks = stats.get('networks', {})
                for interface in networks.values():
                    if isinstance(interface, dict):
                        net_input += interface.get('rx_bytes', 0)
                        net_output += interface.get('tx_bytes', 0)

                result = {
                    "id": container.id[:12],
                    "name": container.name,
                    "cpu": round(cpu_percent, 2),
                    "memory": round(memory_percent, 2),
                    "net_input": net_input,
                    "net_output": net_output
                }
                logger.debug(f"Result for {container.name}: {result}")
                return result
            except Exception as e:
                logger.error(f"Error getting stats for {container.name}: {e}")
                return None

        stats_list = [get_stats_for_container(c) for c in client.containers.list(all=True)]

        return {"stats": [s for s in stats_list if s]}

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)