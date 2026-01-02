"""Configuration management for the application."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    
    # Database Configuration
    database_url: str = "sqlite:///./database/chatbot.db"
    
    # Application Configuration
    app_name: str = "AI Chatbot Service"
    debug: bool = True
    log_level: str = "INFO"
    
    # API Configuration
    max_context_messages: int = 10
    max_tokens: int = 500
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @classmethod
    def get_openai_key(cls) -> str:
        """Get OpenAI API key from environment or SSM Parameter Store."""
        # First try environment variable (set by systemd from SSM)
        key = os.getenv("OPENAI_API_KEY")
        if key and key.strip():
            return key.strip()
        
        # Fallback to .env file for local development
        try:
            temp_settings = cls()
            if temp_settings.openai_api_key:
                return temp_settings.openai_api_key
        except Exception:
            pass
        
        raise ValueError("OPENAI_API_KEY not found in environment or .env file")


# Global settings instance
# This will work with environment variables set by systemd (production)
# or .env file (local development)
# OpenAI API key is optional during initialization (only needed when using OpenAI service)
try:
    # Try to get from environment first (production)
    try:
        openai_key = Settings.get_openai_key()
        settings = Settings(openai_api_key=openai_key)
    except ValueError:
        # OpenAI key not available - that's OK, we'll load it when needed
        settings = Settings()
except Exception as e:
    # Fallback for local development - will use .env file
    # OpenAI key might not be available during data loading, which is OK
    settings = Settings()

