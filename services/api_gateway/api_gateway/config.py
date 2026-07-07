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

    # ---- Admin authentication (for user-management endpoints) ----
    api_gateway_admin_api_key: str = Field(
        ..., alias="API_GATEWAY_ADMIN_API_KEY"
    )

    # ---- User API keys file ----
    api_keys_file: str = Field(
        default="/data/users.json", alias="API_KEYS_FILE"
    )

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
    services_internal_api_key: str = Field(
        ...,
        alias="SERVICES_INTERNAL_API_KEY",
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # --- Optional first user bootstrap ---
    api_gateway_bootstrap_user_api_key: str | None = Field(
        default=None,
        alias="API_GATEWAY_BOOTSTRAP_USER_API_KEY",
    )

    api_gateway_bootstrap_user_name: str | None = Field(
        default=None,
        alias="API_GATEWAY_BOOTSTRAP_USER_NAME",
    )

    api_gateway_bootstrap_user_email: str | None = Field(
        default=None,
        alias="API_GATEWAY_BOOTSTRAP_USER_EMAIL",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper


@lru_cache()
def get_settings() -> ApiGatewaySettings:
    """Get cached settings instance (Singleton pattern)."""
    return ApiGatewaySettings()
