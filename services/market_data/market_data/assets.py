from market_data.enums import DataProvider

_SYMBOL_ALIASES: dict[str, dict[DataProvider, str]] = {
    "btc": {
        DataProvider.COINGECKO: "bitcoin",
        DataProvider.COINCAP: "bitcoin",
    },
    "xbt": {
        DataProvider.COINGECKO: "bitcoin",
        DataProvider.COINCAP: "bitcoin",
    },
    "eth": {
        DataProvider.COINGECKO: "ethereum",
        DataProvider.COINCAP: "ethereum",
    },
    "doge": {
        DataProvider.COINGECKO: "dogecoin",
        DataProvider.COINCAP: "dogecoin",
    },
    "sol": {
        DataProvider.COINGECKO: "solana",
        DataProvider.COINCAP: "solana",
    },
}


def normalize_asset_input(value: str) -> str:
    normalized = value.strip().lower()

    if not normalized:
        raise ValueError("Asset symbol must not be empty")

    return normalized


def resolve_provider_asset_id(value: str, provider: DataProvider) -> str:
    """
    Convert public input into the provider-specific asset identifier.

    Examples:
    - BTC -> bitcoin
    - btc -> bitcoin
    - bitcoin -> bitcoin
    - ETH -> ethereum
    """
    normalized = normalize_asset_input(value)

    provider_aliases = _SYMBOL_ALIASES.get(normalized, {})
    return provider_aliases.get(provider, normalized)
