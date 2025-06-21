from pydantic_settings import BaseSettings
from typing import List
import os

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
    
    # Database Configuration (for future use)
    DATABASE_URL: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 