import pytest
from fastapi import status

API_V1_URL_PREFIX = "/api/v1/seller"


@pytest.mark.asyncio
async def test_create_seller(async_client):
    payload = {
        "first_name": "Ivan",
        "last_name": "Petrov",
        "e_mail": "ivan@example.com",
        "password": "123456",
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["first_name"] == "Ivan"
    assert data["last_name"] == "Petrov"
    assert data["e_mail"] == "ivan@example.com"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_all_sellers(async_client):
    await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json={
            "first_name": "Ivan",
            "last_name": "Petrov",
            "e_mail": "ivan1@example.com",
            "password": "123456",
        },
    )
    await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json={
            "first_name": "Petr",
            "last_name": "Sidorov",
            "e_mail": "petr@example.com",
            "password": "123456",
        },
    )

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "sellers" in data
    assert len(data["sellers"]) == 2
    for seller in data["sellers"]:
        assert "password" not in seller


@pytest.mark.asyncio
async def test_get_single_seller_requires_token(async_client):
    create_response = await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json={
            "first_name": "Ivan",
            "last_name": "Petrov",
            "e_mail": "single@example.com",
            "password": "123456",
        },
    )
    seller_id = create_response.json()["id"]

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller_id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_single_seller_with_token(async_client):
    seller_payload = {
        "first_name": "Ivan",
        "last_name": "Petrov",
        "e_mail": "authseller@example.com",
        "password": "123456",
    }

    create_response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=seller_payload)
    seller_id = create_response.json()["id"]

    token_response = await async_client.post(
        "/api/v1/token/",
        json={
            "e_mail": seller_payload["e_mail"],
            "password": seller_payload["password"],
        },
    )
    token = token_response.json()["access_token"]

    response = await async_client.get(
        f"{API_V1_URL_PREFIX}/{seller_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == seller_id
    assert data["e_mail"] == seller_payload["e_mail"]
    assert "books" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_update_seller(async_client):
    create_response = await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json={
            "first_name": "Ivan",
            "last_name": "Petrov",
            "e_mail": "update@example.com",
            "password": "123456",
        },
    )
    seller_id = create_response.json()["id"]

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller_id}",
        json={
            "first_name": "Updated",
            "last_name": "Seller",
            "e_mail": "updated@example.com",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Seller"
    assert data["e_mail"] == "updated@example.com"
    assert "password" not in data


@pytest.mark.asyncio
async def test_delete_seller_and_books(async_client):
    seller_payload = {
        "first_name": "Ivan",
        "last_name": "Petrov",
        "e_mail": "deletecascade@example.com",
        "password": "123456",
    }

    create_seller_response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=seller_payload)
    seller_id = create_seller_response.json()["id"]

    token_response = await async_client.post(
        "/api/v1/token/",
        json={
            "e_mail": seller_payload["e_mail"],
            "password": seller_payload["password"],
        },
    )
    token = token_response.json()["access_token"]

    create_book_response = await async_client.post(
        "/api/v1/books/",
        json={
            "title": "Test Book",
            "author": "Author",
            "year": 2024,
            "count_pages": 200,
            "seller_id": seller_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    book_id = create_book_response.json()["id"]

    delete_response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    get_book_response = await async_client.get(f"/api/v1/books/{book_id}")
    assert get_book_response.status_code == status.HTTP_404_NOT_FOUND