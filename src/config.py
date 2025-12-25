"""Configuration management for the application."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
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


# Global settings instance
settings = Settings()

