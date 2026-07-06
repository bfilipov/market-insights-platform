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
    └── market_data/             # Internal data fetching service
```

### Configuration

1. Copy the example environment file:
    ```
    cp .env.example .env
    ```
2. Edit the .env file and set the required variables:
    ```
    API_GATEWAY_ADMIN_API_KEY: Secret key used to manage API users.
    MARKET_DATA_INTERNAL_API_KEY: Shared secret for internal service-to-service communication.
    COINCAP_API_KEY: Your API key for the CoinCap service.
    ```

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

    Market data endpoints require a valid user API key.    

    #### Fetch market data for a specific asset:
    ```
   curl http://localhost:8000/api/v1/market/bitcoin \
    -H "Authorization: Bearer YOUR_USER_API_KEY"
   ```
    #### Override the default data provider:
    ```
    curl "http://localhost:8000/api/v1/market/bitcoin?provider=coincap" \
    -H "Authorization: Bearer YOUR_USER_API_KEY"
   ```
   #### Missing Authentication (Expected: 401)
    ```
    curl http://localhost:8000/api/v1/market/bitcoin
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
