def test_create_inventory(client):
    product_data = {
        "sku": "INVENTORY-TEST-001",
        "name": "Inventory Test Product",
        "description": "Product for inventory testing",
        "unit_price": 10000,
        "currency": "INR",
    }

    product_response = client.post(
        "/api/v1/products",
        json=product_data,
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    inventory_data = {
        "product_id": product_id,
        "warehouse_code": "TEST-WH01",
        "quantity_on_hand": 50,
        "quantity_reserved": 5,
        "reorder_level": 10,
    }

    response = client.post(
        "/api/v1/inventory",
        json=inventory_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["product_id"] == product_id
    assert data["warehouse_code"] == "TEST-WH01"
    assert data["quantity_on_hand"] == 50
    assert data["quantity_reserved"] == 5


def test_duplicate_inventory_rejected(client):
    product_data = {
        "sku": "INVENTORY-DUPLICATE-001",
        "name": "Duplicate Inventory Product",
        "description": "Testing duplicate inventory",
        "unit_price": 15000,
        "currency": "INR",
    }

    product_response = client.post(
        "/api/v1/products",
        json=product_data,
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    inventory_data = {
        "product_id": product_id,
        "warehouse_code": "TEST-WH01",
        "quantity_on_hand": 30,
        "quantity_reserved": 0,
        "reorder_level": 5,
    }

    first_response = client.post(
        "/api/v1/inventory",
        json=inventory_data,
    )

    second_response = client.post(
        "/api/v1/inventory",
        json=inventory_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "Inventory already exists for this product and warehouse"
    )
