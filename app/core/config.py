import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQL_SERVER: str = os.getenv("SQL_SERVER", "localhost")
    SQL_DATABASE: str = os.getenv("SQL_DATABASE", "master")
    SQL_USER: str = os.getenv("SQL_USER", "sa")
    SQL_PASSWORD: str = os.getenv("SQL_PASSWORD", "tu_password")
    # Conexión a Redis en Docker
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # URL base para el worker (usar host.docker.internal en Docker)
    API_BASE_URL: str = "http://localhost:8000"
    # Configuración de Celery Worker
    CELERY_CONCURRENCY: int = 4
    CELERY_MAX_TASKS_PER_CHILD: int = 100
    CELERY_MAX_MEMORY_MB: int = 300  # MB
    CELERY_QUEUES: str = "transfers,monitoring"
    CELERY_WORKER_PREFIX: str = "db_worker"
    CELERY_LOG_LEVEL: str = "INFO"
    class Config:
        env_file = ".env"

settings = Settings()
