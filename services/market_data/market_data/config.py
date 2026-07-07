"""
Configuration for the Market Data Service.

Uses python-dotenv to explicitly load the .env file into os.environ,
and standard Pydantic BaseModel to parse those environment variables.
This avoids pydantic-settings file-path resolution issues.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from market_data.enums import DataProvider


class MarketDataConfig(BaseSettings):
    """
    Configuration settings loaded directly from os.environ.

    We use aliases to map PEP8 Python variables to UPPER_CASE env vars.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server Configuration
    market_data_host: str = Field("0.0.0.0", alias="MARKET_DATA_HOST")
    market_data_port: int = Field(8001, alias="MARKET_DATA_PORT")

    # Internal Authentication
    services_internal_api_key: str = Field(..., alias="SERVICES_INTERNAL_API_KEY")

    # Provider Configuration
    market_data_default_provider: DataProvider = Field(
        DataProvider.COINGECKO, alias="MARKET_DATA_DEFAULT_PROVIDER"
    )

    # External Provider URLs
    coingecko_base_url: str = Field(
        "https://api.coingecko.com/api/v3", alias="COINGECKO_BASE_URL"
    )
    coincap_base_url: str = Field(
        "https://rest.coincap.io/v3", alias="COINCAP_BASE_URL"
    )

    # External Provider API keys
    coincap_api_key: str = Field(..., alias="COINCAP_API_KEY")

    # Resilience Configuration
    market_data_request_timeout: float = Field(
        10.0, alias="MARKET_DATA_REQUEST_TIMEOUT", ge=1.0
    )
    market_data_max_retries: int = Field(
        3, alias="MARKET_DATA_MAX_RETRIES", ge=1
    )

    # Logging
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    @field_validator("log_level", mode="before")
    @classmethod
    def uppercase_log_level(cls, v: str) -> str:
        if isinstance(v, str):
            return v.upper()
        return v


# 3. Singleton instance getter
def get_settings() -> MarketDataConfig:
    """Get the configuration instance."""
    # Because we already loaded dotenv, we just instantiate the model.
    # It will automatically read from os.environ.
    return MarketDataConfig()
