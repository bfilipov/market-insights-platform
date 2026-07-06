"""Enumerations for the Market Data Service."""

import enum


class DataProvider(str, enum.Enum):
    """Supported external market data providers."""

    COINGECKO = "coingecko"
    COINCAP = "coincap"
