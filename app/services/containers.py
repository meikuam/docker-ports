from typing import List, Dict, Any

from app.services.docker_client import get_docker_client


def list_containers_data() -> List[Dict[str, Any]]:
    """List all containers with their port bindings"""
    client = get_docker_client()
    containers = client.containers.list(all=True)
    containers_data = []

    for container in containers:
        container_id = None
        try:
            container_id = str(container.id)[:12]
        except AttributeError:
            container_id = "unknown"

        container_info = {
            "id": container_id,
            "name": container.name or "unknown",
            "status": container.status or "unknown",
            "ports": [],
        }

        image = None
        if container.image:
            try:
                image = (
                    container.image.tags[0]
                    if container.image and container.image.tags
                    else None
                )
            except (AttributeError, IndexError, TypeError):
                image = None

            container_info["image"] = image

        ports = container.attrs.get("NetworkSettings", {}).get("Ports") or {}
        if isinstance(ports, dict) and ports:
            for container_port, host_bindings in ports.items():
                if isinstance(host_bindings, list):
                    bindings = []
                    for binding in host_bindings:
                        if binding and isinstance(binding, dict):
                            host_port = binding.get("HostPort")
                            ip_address = binding.get("HostIp", "0.0.0.0")
                            bindings.append(
                                f"{ip_address}:{host_port}"
                                if host_port
                                else ip_address
                            )
                    container_info["ports"].append(
                        {
                            "container_port": container_port,
                            "host_bindings": bindings,
                        }
                    )

        containers_data.append(container_info)

    return containers_data