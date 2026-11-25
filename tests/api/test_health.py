def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "S4Bridge"
    assert response.json()["status"] == "healthy"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "S4Bridge API"
