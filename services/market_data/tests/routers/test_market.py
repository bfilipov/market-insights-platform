async def test_health_check_no_auth_required(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "market-data"


async def test_market_data_unauthorized_missing_header(client):
    response = await client.get("/api/v1/market/bitcoin")
    assert response.status_code == 401


async def test_market_data_unauthorized_invalid_key(client):
    headers = {"Authorization": "Bearer wrong-key"}
    response = await client.get("/api/v1/market/bitcoin", headers=headers)
    assert response.status_code == 401


async def test_market_data_success(client):
    headers = {"Authorization": "Bearer test-internal-key"}
    response = await client.get("/api/v1/market/bitcoin", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "bitcoin"
    assert data["name"] == "Bitcoin"
    assert data["current_price_usd"] == 100.0
    assert data["data_source"] == "mock"


async def test_market_data_asset_not_found(client):
    headers = {"Authorization": "Bearer test-internal-key"}
    response = await client.get("/api/v1/market/notfound", headers=headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


async def test_market_data_service_unavailable(client):
    headers = {"Authorization": "Bearer test-internal-key"}
    response = await client.get("/api/v1/market/unavailable", headers=headers)

    assert response.status_code == 503
    assert "temporarily unavailable" in response.json()["detail"]


async def test_market_data_unsupported_provider(client):
    headers = {"Authorization": "Bearer test-internal-key"}
    response = await client.get(
        "/api/v1/market/bitcoin",
        headers=headers,
        params={"provider": "invalid_provider"}
    )

    # FastAPI validates the Enum type before the request hits the endpoint logic,
    # resulting in a 422 Unprocessable Entity response.
    assert response.status_code == 422
