from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MarketSignalConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    market_signal_host: str = Field("0.0.0.0", alias="MARKET_SIGNAL_HOST")
    market_signal_port: int = Field(8002, alias="MARKET_SIGNAL_PORT")
    market_signal_internal_api_key: str = Field(..., alias="SERVICES_INTERNAL_API_KEY")
    log_level: str = Field("INFO", alias="LOG_LEVEL")


def get_settings() -> MarketSignalConfig:
    return MarketSignalConfig()
