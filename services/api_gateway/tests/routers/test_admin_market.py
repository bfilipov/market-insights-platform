# ==========================================
# Admin Router Tests
# ==========================================
from api_gateway.services.market_service import MarketService
from tests.conftest import MockMarketDataClient


async def test_admin_create_user_unauthorized(client):
    response = await client.post("/api/v1/admin/users", json={"name": "Test"})
    assert response.status_code == 401


async def test_admin_create_user_success(client):
    headers = {"Authorization": "Bearer test-admin-key"}
    response = await client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={"name": "New User", "email": "new@test.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New User"
    assert "api_key" in data
    assert data["is_active"] is True


async def test_admin_list_users_hides_api_keys(client, user_store):
    headers = {"Authorization": "Bearer test-admin-key"}
    user_store.add_user(name="Existing User")

    response = await client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # Ensure API keys are never exposed in list view
    assert "api_key" not in data[0]


async def test_admin_deactivate_user(client, user_store):
    headers = {"Authorization": "Bearer test-admin-key"}
    user = user_store.add_user(name="To Deactivate")

    response = await client.patch(
        f"/api/v1/admin/users/{user.id}/deactivate", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


async def test_admin_delete_user(client, user_store):
    headers = {"Authorization": "Bearer test-admin-key"}
    user = user_store.add_user(name="To Delete")

    response = await client.delete(
        f"/api/v1/admin/users/{user.id}", headers=headers
    )
    assert response.status_code == 200
    assert user_store.get_user(user.id) is None


# ==========================================
# Market Router Tests
# ==========================================

async def test_market_unauthorized_missing_header(client):
    response = await client.get("/api/v1/market/bitcoin")
    assert response.status_code == 401


async def test_market_unauthorized_invalid_key(client):
    headers = {"Authorization": "Bearer invalid-key"}
    response = await client.get("/api/v1/market/bitcoin", headers=headers)
    assert response.status_code == 401


async def test_market_success_with_user_key(client, user_store):
    user = user_store.add_user(name="Market User")
    headers = {"Authorization": f"Bearer {user.api_key}"}

    response = await client.get("/api/v1/market/bitcoin", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "bitcoin"
    assert data["name"] == "Bitcoin"
    assert data["current_price_usd"] == 100.0


async def test_market_fails_with_inactive_user_key(client, user_store):
    user = user_store.add_user(name="Inactive Market User")
    user_store.deactivate_user(user.id)

    headers = {"Authorization": f"Bearer {user.api_key}"}
    response = await client.get("/api/v1/market/bitcoin", headers=headers)
    assert response.status_code == 401


async def test_health_check_works_without_auth(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


async def test_market_success_without_signal(client, user_store):
    """Ensure the original endpoint does not return signals."""
    user = user_store.add_user(name="Market User")
    headers = {"Authorization": f"Bearer {user.api_key}"}

    response = await client.get("/api/v1/market/bitcoin", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "bitcoin"
    # Verify signal fields are not present in the base response
    assert "market_signal" not in data
    assert "disclaimer" not in data


async def test_market_insights_success_with_signal(client, user_store, mock_market_signal_client_success):
    """Ensure the new endpoint returns combined data."""
    from api_gateway.dependencies import get_market_signal_client
    client.app.dependency_overrides[get_market_signal_client] = lambda: mock_market_signal_client_success

    user = user_store.add_user(name="Insights User")
    headers = {"Authorization": f"Bearer {user.api_key}"}

    response = await client.get("/api/v1/market/bitcoin/insights", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "bitcoin"
    assert data["market_signal"] is not None
    assert data["market_signal"]["signal"] == "bullish"
    assert data["disclaimer"] is not None

    client.app.dependency_overrides.pop(get_market_signal_client, None)


async def test_market_insights_graceful_degradation(client, user_store, mock_market_signal_client_fail):
    """Ensure the new endpoint still works if Service C fails."""
    from api_gateway.dependencies import get_market_service

    # Create a specific MarketService instance using the FAILING mock
    failing_market_service = MarketService(
        market_data_client=MockMarketDataClient(),
        market_signal_client=mock_market_signal_client_fail  # Inject the failing one here
    )

    # Override the MarketService dependency for this specific test
    client.app.dependency_overrides[get_market_service] = lambda: failing_market_service

    user = user_store.add_user(name="Insights User")
    headers = {"Authorization": f"Bearer {user.api_key}"}

    response = await client.get("/api/v1/market/bitcoin/insights", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "bitcoin"
    assert data["market_signal"] is None
    assert data["disclaimer"] is None
