"""
Application Configuration Management
Centralized configuration using Pydantic Settings
"""
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # DeepSeek API Configuration
    deepseek_api_key: str = Field(
        ...,
        description="DeepSeek API key for LLM access"
    )
    deepseek_api_base: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API base URL"
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="DeepSeek model name"
    )
    deepseek_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model temperature for response randomness"
    )
    
    # Google Cloud Configuration
    google_cloud_auth_email: str = Field(
        ...,
        description="Google Cloud authenticated email address"
    )
    google_credentials_path: Path = Field(
        default=Path("creds/credentials.json"),
        description="Path to Google OAuth credentials file"
    )
    google_token_path: Path = Field(
        default=Path("token.pickle"),
        description="Path to Google OAuth token cache"
    )
    google_calendar_timezone: str = Field(
        default="America/Los_Angeles",
        description="Default timezone for calendar events"
    )
    
    # Rate Limiting Configuration
    rate_limit_requests_per_second: float = Field(
        default=0.2,
        gt=0.0,
        description="Maximum requests per second for API calls"
    )
    rate_limit_check_interval: float = Field(
        default=0.1,
        gt=0.0,
        description="Interval to check rate limit (seconds)"
    )
    rate_limit_max_burst: int = Field(
        default=10,
        gt=0,
        description="Maximum burst size for rate limiting"
    )
    
    @field_validator("google_credentials_path", "google_token_path")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        """Ensure paths are Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    def get_google_scopes(self) -> list[str]:
        """Return the list of required Google API scopes."""
        return [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/documents'
        ]


# Global settings instance
settings = Settings()
