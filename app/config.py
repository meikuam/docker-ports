from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment"""

    title: str = "Docker Ports Viewer"
    version: str = "1.0.0"

    docker_host: str = "unix:///var/run/docker.sock"
    docker_tls_verify: str = "0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()