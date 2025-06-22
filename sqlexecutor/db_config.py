from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class DatabaseConfig(BaseSettings):
    """Database configuration for Aiven PostgreSQL"""
    
    # Database connection details
    DB_HOST: str = "data-simulation-mirrormatch375-1854.i.aivencloud.com"
    DB_PORT: int = 19273  # Updated to the correct Aiven port
    DB_NAME: str = "telemetrysimulation"  # Update this with your actual database name
    DB_USER: str = "avnadmin"
    DB_PASSWORD: str = ""
    
    # Connection options
    DB_SSL_MODE: str = "require"  # Aiven requires SSL
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Timeout settings
    DB_CONNECT_TIMEOUT: int = 10
    DB_QUERY_TIMEOUT: int = 30
    
    @property
    def database_url(self) -> str:
        """Generate database URL from components"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSL_MODE}"
    
    @property
    def connection_params(self) -> dict:
        """Get connection parameters as dictionary"""
        return {
            "host": self.DB_HOST,
            "port": self.DB_PORT,
            "database": self.DB_NAME,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "sslmode": self.DB_SSL_MODE
        }
    
    class Config:
        # Look for .env file in the api_server directory
        env_file = str(Path(__file__).parent.parent / "api_server" / ".env")
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env file

# Create database config instance
db_config = DatabaseConfig() 