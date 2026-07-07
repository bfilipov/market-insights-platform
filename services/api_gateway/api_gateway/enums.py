import enum


class DataProvider(str, enum.Enum):
    COINGECKO = "coingecko"
    COINCAP = "coincap"
