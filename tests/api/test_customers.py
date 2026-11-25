def test_create_customer(client):
    customer_data = {
        "company_name": "Automated Test Company",
        "contact_name": "Test User",
        "email": "automated.test@s4bridge.com",
        "phone": "9876501111",
    }

    response = client.post(
        "/api/v1/customers",
        json=customer_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["company_name"] == "Automated Test Company"
    assert data["email"] == "automated.test@s4bridge.com"
    assert data["status"] == "active"
    assert data["id"] > 0


def test_duplicate_customer_email(client):
    customer_data = {
        "company_name": "Automated Test Company",
        "contact_name": "Test User",
        "email": "duplicate.test@s4bridge.com",
        "phone": "9876501111",
    }

    first_response = client.post(
        "/api/v1/customers",
        json=customer_data,
    )

    second_response = client.post(
        "/api/v1/customers",
        json=customer_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"] == "A customer with this email already exists"
    )
