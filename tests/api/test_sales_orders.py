def create_order_test_data(client):
    customer_response = client.post(
        "/api/v1/customers",
        json={
            "company_name": "Sales Order Test Company",
            "contact_name": "Order Test User",
            "email": "sales.order.test@s4bridge.com",
            "phone": "9876502222",
        },
    )

    assert customer_response.status_code == 201
    customer_id = customer_response.json()["id"]

    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "ORDER-TEST-001",
            "name": "Order Test Product",
            "description": "Product for sales order testing",
            "unit_price": 1000,
            "currency": "INR",
        },
    )

    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    inventory_response = client.post(
        "/api/v1/inventory",
        json={
            "product_id": product_id,
            "warehouse_code": "TEST-WH01",
            "quantity_on_hand": 20,
            "quantity_reserved": 0,
            "reorder_level": 5,
        },
    )

    assert inventory_response.status_code == 201

    return customer_id, product_id


def test_create_sales_order_and_reserve_inventory(client):
    customer_id, product_id = create_order_test_data(client)

    order_response = client.post(
        "/api/v1/sales-orders",
        json={
            "customer_id": customer_id,
            "warehouse_code": "TEST-WH01",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 3,
                }
            ],
        },
    )

    assert order_response.status_code == 201

    order = order_response.json()

    assert order["customer_id"] == customer_id
    assert order["status"] == "pending"
    assert float(order["total_amount"]) == 3000.00
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 3

    inventory_response = client.get(
        f"/api/v1/inventory/product/{product_id}",
        params={"warehouse_code": "TEST-WH01"},
    )

    assert inventory_response.status_code == 200

    inventory = inventory_response.json()[0]

    assert inventory["quantity_on_hand"] == 20
    assert inventory["quantity_reserved"] == 3


def test_sales_order_rejects_insufficient_stock(client):
    customer_id, product_id = create_order_test_data(client)

    order_response = client.post(
        "/api/v1/sales-orders",
        json={
            "customer_id": customer_id,
            "warehouse_code": "TEST-WH01",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 25,
                }
            ],
        },
    )

    assert order_response.status_code == 400

    assert "Insufficient stock" in order_response.json()["detail"]

    inventory_response = client.get(
        f"/api/v1/inventory/product/{product_id}",
        params={"warehouse_code": "TEST-WH01"},
    )

    inventory = inventory_response.json()[0]

    assert inventory["quantity_reserved"] == 0
