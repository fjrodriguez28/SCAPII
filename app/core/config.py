import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQL_SERVER: str = os.getenv("SQL_SERVER", "localhost")
    SQL_DATABASE: str = os.getenv("SQL_DATABASE", "master")
    SQL_USER: str = os.getenv("SQL_USER", "sa")
    SQL_PASSWORD: str = os.getenv("SQL_PASSWORD", "tu_password")
    
    class Config:
        env_file = ".env"

settings = Settings()
