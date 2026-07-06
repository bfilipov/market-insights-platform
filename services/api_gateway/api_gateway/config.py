from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiGatewaySettings(BaseSettings):
    """Configuration settings for the API Gateway service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server configuration
    api_gateway_host: str = Field(default="0.0.0.0", alias="API_GATEWAY_HOST")
    api_gateway_port: int = Field(default=8000, alias="API_GATEWAY_PORT")

    # Authentication
    api_gateway_api_key: str = Field(..., alias="API_GATEWAY_API_KEY")

    # Service URLs
    market_data_service_url: str = Field(
        default="http://localhost:8001",
        alias="MARKET_DATA_SERVICE_URL",
    )
    market_signal_service_url: str = Field(
        default="http://localhost:8002",
        alias="MARKET_SIGNAL_SERVICE_URL",
    )

    # Internal service authentication
    market_data_internal_api_key: str = Field(
        ...,
        alias="MARKET_DATA_INTERNAL_API_KEY",
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    @field_validator("api_gateway_api_key")
    @classmethod
    def validate_api_key_not_placeholder(cls, v: str) -> str:
        """Ensure API key is not a placeholder value."""
        placeholder_values = {"your-secure-api-key-here", "change-me", "placeholder"}
        if v.lower() in placeholder_values:
            raise ValueError("API key must be changed from placeholder value")
        return v


@lru_cache()
def get_settings() -> ApiGatewaySettings:
    """
    Get cached settings instance (Singleton pattern).

    Uses lru_cache to ensure settings are loaded and validated only once,
    then shared across all calls.
    """
    return ApiGatewaySettings()