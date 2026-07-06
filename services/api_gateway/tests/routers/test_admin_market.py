# ==========================================
# Admin Router Tests
# ==========================================

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
