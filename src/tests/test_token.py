import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_get_token(async_client):
    seller_payload = {
        "first_name": "Token",
        "last_name": "User",
        "e_mail": "tokenuser@example.com",
        "password": "123456",
    }

    await async_client.post("/api/v1/seller/", json=seller_payload)

    response = await async_client.post(
        "/api/v1/token/",
        json={
            "e_mail": seller_payload["e_mail"],
            "password": seller_payload["password"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_token_with_wrong_password(async_client):
    seller_payload = {
        "first_name": "Token",
        "last_name": "User",
        "e_mail": "wrongpass@example.com",
        "password": "123456",
    }

    await async_client.post("/api/v1/seller/", json=seller_payload)

    response = await async_client.post(
        "/api/v1/token/",
        json={
            "e_mail": seller_payload["e_mail"],
            "password": "wrong_password",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED