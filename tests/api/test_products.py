def test_create_product(client):
    product_data = {
        "sku": "AUTO-TEST-001",
        "name": "Automated Test Laptop",
        "description": "Product created by automated tests",
        "unit_price": 50000,
        "currency": "INR",
    }

    response = client.post(
        "/api/v1/products",
        json=product_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["sku"] == "AUTO-TEST-001"
    assert data["name"] == "Automated Test Laptop"
    assert float(data["unit_price"]) == 50000.00
    assert data["currency"] == "INR"
    assert data["is_active"] is True


def test_duplicate_product_sku(client):
    product_data = {
        "sku": "AUTO-DUPLICATE-001",
        "name": "Duplicate Test Product",
        "description": "Testing duplicate SKU validation",
        "unit_price": 25000,
        "currency": "INR",
    }

    first_response = client.post(
        "/api/v1/products",
        json=product_data,
    )

    second_response = client.post(
        "/api/v1/products",
        json=product_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == "A product with this SKU already exists"
