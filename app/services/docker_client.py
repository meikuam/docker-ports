import docker


def get_docker_client():
    """Get Docker client"""
    return docker.from_env()