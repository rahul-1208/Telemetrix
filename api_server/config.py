from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "SaaS Product Usage Data Assistant"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]  # Configure for production
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""  # Load from environment variable
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 1000
    
    # Database Configuration
    DATABASE_URL: str = ""
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_SSL_MODE: str = "require"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        # Look for .env file in the api_server directory
        env_file = str(Path(__file__).parent / ".env")
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env file

# Create settings instance
settings = Settings() 