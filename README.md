# Market Insights Platform
A microservices-based platform for fetching and normalizing cryptocurrency market data. The system consists of an API Gateway that handles external request authentication and a Market Data Service that integrates with third-party providers (CoinGecko, CoinCap).

### External API Choices
This platform integrates with two public cryptocurrency APIs:

CoinGecko API: Chosen because it has a generous free tier and does not require an API key for basic market data queries.   
CoinCap API: Used as a secondary provider. It requires a free API key, which aligns with the requirement to handle authenticated external integrations.   


### Prerequisites
- Docker
- Docker Compose
= Python 3.12+ and Poetry (optional, for running tests locally)
- Project Structure

### Project structure
```
.
├── docker-compose.yml
├── .env.example
├── data/
│   └── users.json               # Auto-generated API user credentials
└── services/
    ├── api_gateway/             # Public-facing REST API
    ├── market_data/             # Internal data fetching service
    └── market_signal/           # Rule-based market signal generation
```

### Configuration

1. Copy the example environment file:
    ```
    cp .env.example .env
    ```
2. Edit the .env file and set the required variables:
    ```
    API_GATEWAY_ADMIN_API_KEY: Secret key used to manage API users.
    SERVICES_INTERNAL_API_KEY: Shared secret for internal service-to-service communication.
    COINCAP_API_KEY: Your API key for the CoinCap service.
    ```

### Authentication model

The API Gateway uses two kinds of API keys:

1. Admin API key

   `API_GATEWAY_ADMIN_API_KEY`

   This key is configured through `.env` and is used only for user-management endpoints under `/api/v1/admin`.

2. User API keys

   User API keys are used by clients calling `/api/v1/market/*`.

   User keys can be created in two ways:

   - Recommended: call `POST /api/v1/admin/users` with the admin key.
   - Optional local bootstrap: set `API_GATEWAY_BOOTSTRAP_USER_API_KEY` before first startup. If `data/users.json` is empty, the API Gateway creates one initial user with this key.

The bootstrap key is only used when the user store is empty. Once `data/users.json` exists, changing `API_GATEWAY_BOOTSTRAP_USER_API_KEY` does not rotate existing users. Use the admin regenerate endpoint for key rotation.


### Running the Application
Start all services using Docker Compose:   
```
docker-compose up --build
```

The API Gateway will be available at http://localhost:8000.

### Usage
1. User Management (Admin API)   
    Admin endpoints require the API_GATEWAY_ADMIN_API_KEY defined in your .env file.   
    Create a new API user:

    ```
    curl -X POST http://localhost:8000/api/v1/admin/users \
    -H "Authorization: Bearer YOUR_ADMIN_KEY" \
    -H "Content-Type: application/json" \
    -d '{"name": "Service Account", "email": "service@example.com"}'
    ```

    The response will contain the generated api_key. This key is only shown once.

    List current users:
    ```
    curl http://localhost:8000/api/v1/admin/users \
    -H "Authorization: Bearer YOUR_ADMIN_KEY"
    ```
   
2. Querying Market Data

    #### Asset identifiers
 
    The public market endpoints accept either:
 
   - a common crypto ticker alias, for example `BTC`, `ETH`, `DOGE`, `SOL`;
   - a provider asset id, for example `bitcoin`, `ethereum`, `dogecoin`, `solana`.
   
    - Ticker aliases are resolved inside the Market Data Service before calling the external provider.

    #### Fetch market data for a specific asset (Market data endpoints require a valid user API key. ):
    ```
   curl http://localhost:8000/api/v1/market/BTC \
    -H "Authorization: Bearer YOUR_USER_API_KEY"
   ```
   
    #### Exaple request with Asset Id instead of symbol:
    ```
   curl http://localhost:8000/api/v1/market/bitcoin \
    -H "Authorization: Bearer YOUR_USER_API_KEY"
   ```
    #### Override the default data provider:
    ```
    curl "http://localhost:8000/api/v1/market/BTC?provider=coincap" \
    -H "Authorization: Bearer YOUR_USER_API_KEY"
   ```
   
    #### Fetch market data with rule-based signals:
    ```
    curl "http://localhost:8000/api/v1/market/BTC/insights" \
    -H "Authorization: Bearer YOUR_USER_API_KEY"
   ```   

   #### Example response: 
    ```
    {
      "symbol": "btc",
      "name": "Bitcoin",
      "current_price_usd": 43250.75,
      "market_cap_usd": 847500000000,
      "price_change_24h_usd": 1250.50,
      "price_change_percentage_24h": 2.97,
      "high_24h_usd": 44000.00,
      "low_24h_usd": 42000.00,
      "last_updated": "2025-01-01T12:00:00Z",
      "data_source": "coingecko",
      "market_signal": {
        "signal": "bullish",
        "rule_description": "24h change is +2.97% (> +2%)"
      },
      "disclaimer": "Rule-based indicator, not financial advice."
    }
   ```
   
   #### Missing Authentication (Expected: 401)
    ```
    curl http://localhost:8000/api/v1/market/BTC
   ```

### Running Tests
Unit tests for the API Gateway are included to verify API key management and routing logic.

To run tests locally:

1. Navigate to the service directory, e.g:

    ```
    cd services/api_gateway
    ```
   
2. Install dependencies:
    ```
    poetry install
   ```
3. Execute the test suite:
    ```
    poetry run pytest
   ```
