async def test_signal_unauthorized_missing_header(client):
    response = await client.post("/api/v1/signal", json={"symbol": "btc"})
    assert response.status_code == 401


async def test_signal_unauthorized_invalid_key(client):
    headers = {"Authorization": "Bearer wrong-key"}
    response = await client.post("/api/v1/signal", json={"symbol": "btc"}, headers=headers)
    assert response.status_code == 401


async def test_signal_bullish(client):
    headers = {"Authorization": "Bearer test-internal-key"}
    payload = {"symbol": "btc", "price_change_percentage_24h": 5.0}
    response = await client.post("/api/v1/signal", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == "bullish"
    assert "> +2%" in data["rule_description"]
    assert "not financial advice" in data["disclaimer"]


async def test_signal_bearish(client):
    headers = {"Authorization": "Bearer test-internal-key"}
    payload = {"symbol": "btc", "price_change_percentage_24h": -3.5}
    response = await client.post("/api/v1/signal", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == "bearish"
    assert "< -2%" in data["rule_description"]


async def test_signal_neutral(client):
    headers = {"Authorization": "Bearer test-internal-key"}
    payload = {"symbol": "btc", "price_change_percentage_24h": 1.0}
    response = await client.post("/api/v1/signal", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == "neutral"
    assert "between -2% and +2%" in data["rule_description"]


async def test_signal_missing_data(client):
    headers = {"Authorization": "Bearer test-internal-key"}
    payload = {"symbol": "btc", "price_change_percentage_24h": None}
    response = await client.post("/api/v1/signal", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == "neutral"
    assert "Insufficient data" in data["rule_description"]
