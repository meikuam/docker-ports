import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment"""

    title = os.getenv("APP_TITLE")
    version = os.getenv("APP_VERSION")

    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT", "8000"))

    docker_host = os.getenv("DOCKER_HOST")
    docker_tls_verify = os.getenv("DOCKER_TLS_VERIFY", "")
    docker_cert_path = os.getenv("DOCKER_CERT_PATH") or ""


settings = Settings()
