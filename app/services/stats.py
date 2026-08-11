from typing import List, Dict, Any

from app.services.docker_client import get_docker_client


def get_stats_data() -> List[Dict[str, Any]]:
    """Get CPU/Memory statistics from containers"""
    client = get_docker_client()

    def get_stats_for_container(container):
        try:
            stats = container.stats(stream=False)

            cpu_percent = 0
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            if cpu_stats and "cpu_usage" in cpu_stats:
                cpu_usage = cpu_stats["cpu_usage"]
                percpu_usage = cpu_stats.get("percpu_usage", [])

                if precpu_stats and "cpu_usage" in precpu_stats:
                    precpu_usage = precpu_stats["cpu_usage"]
                    precpu_percpu_usage = precpu_stats.get("percpu_usage", [])

                    if "total_usage" in cpu_usage and "total_usage" in precpu_usage:
                        percpu_delta = sum(precpu_percpu_usage) - sum(percpu_usage)

                        system_delta = cpu_usage.get(
                            "system_cpu_usage", 0
                        ) - precpu_usage.get(
                            "system_cpu_usage", cpu_usage.get("system_cpu_usage", 0)
                        )

                        if system_delta > 0:
                            cpu_percent = (percpu_delta / system_delta) * 100
                        else:
                            cpu_percent = max(0, percpu_delta)

            memory_percent = 0
            memory_stats = stats.get("memory_stats", {})
            if "limit" in memory_stats and memory_stats["limit"] > 0:
                memory_percent = (
                    memory_stats.get("usage", 0) / memory_stats["limit"] * 100
                )

            net_input = 0
            net_output = 0
            networks = stats.get("networks", {})
            for interface in networks.values():
                if isinstance(interface, dict):
                    net_input += interface.get("rx_bytes", 0)
                    net_output += interface.get("tx_bytes", 0)

            result = {
                "id": container.id[:12],
                "name": container.name,
                "cpu": round(cpu_percent, 2),
                "memory": round(memory_percent, 2),
                "net_input": net_input,
                "net_output": net_output,
            }
            return result
        except Exception:
            return None

    stats_list = [
        get_stats_for_container(c) for c in client.containers.list(all=True)
    ]

    return [s for s in stats_list if s]