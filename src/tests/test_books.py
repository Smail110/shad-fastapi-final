import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/books"


async def create_seller_and_token(async_client, email="bookuser@example.com"):
    seller_payload = {
        "first_name": "Book",
        "last_name": "Seller",
        "e_mail": email,
        "password": "123456",
    }

    create_seller_response = await async_client.post("/api/v1/seller/", json=seller_payload)
    seller_id = create_seller_response.json()["id"]

    token_response = await async_client.post(
        "/api/v1/token/",
        json={
            "e_mail": seller_payload["e_mail"],
            "password": seller_payload["password"],
        },
    )
    token = token_response.json()["access_token"]

    return seller_id, token


@pytest.mark.asyncio
async def test_create_book_requires_token(async_client):
    payload = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
        "seller_id": 1,
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_book(async_client):
    seller_id, token = await create_seller_and_token(async_client, "createbook@example.com")

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
        "seller_id": seller_id,
    }

    response = await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_book_id = result_data.pop("id", None)
    assert resp_book_id is not None, "Book id not returned from endpoint"

    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": seller_id,
    }


@pytest.mark.asyncio
async def test_create_book_with_old_year(async_client):
    seller_id, token = await create_seller_and_token(async_client, "oldyear@example.com")

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,
        "seller_id": seller_id,
    }

    response = await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="seller_get_books@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=seller.id,
    )
    book_2 = Book(
        author="Lermontov",
        title="Mziri",
        year=2021,
        pages=108,
        seller_id=seller.id,
    )

    db_session.add_all([book, book_2])
    await db_session.flush()
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["books"]) == 2

    assert response.json() == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2021,
                "id": book.id,
                "pages": 104,
                "seller_id": seller.id,
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 2021,
                "id": book_2.id,
                "pages": 108,
                "seller_id": seller.id,
            },
        ]
    }


@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="single_book_seller@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=seller.id,
    )
    book_2 = Book(
        author="Lermontov",
        title="Mziri",
        year=2021,
        pages=104,
        seller_id=seller.id,
    )

    db_session.add_all([book, book_2])
    await db_session.flush()
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2021,
        "pages": 104,
        "id": book.id,
        "seller_id": seller.id,
    }


@pytest.mark.asyncio
async def test_get_single_book_with_wrong_id(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="wrongid_seller@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=seller.id,
    )

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/426548")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_book_requires_token(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="update_requires_token@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=seller.id,
    )
    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    data = {
        "title": "Mziri",
        "author": "Lermontov",
        "pages": 250,
        "year": 2024,
        "id": book.id,
        "seller_id": seller.id,
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{book.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_book(async_client, db_session):
    seller_id, token = await create_seller_and_token(async_client, "updatebook@example.com")

    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=seller_id,
    )
    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    data = {
        "title": "Mziri",
        "author": "Lermontov",
        "pages": 250,
        "year": 2024,
        "id": book.id,
        "seller_id": seller_id,
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{book.id}",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    await db_session.refresh(book)

    assert book.title == "Mziri"
    assert book.author == "Lermontov"
    assert book.pages == 250
    assert book.year == 2024
    assert book.id == book.id
    assert book.seller_id == seller_id


@pytest.mark.asyncio
async def test_patch_book(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="patch_seller@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        author="Lermontov",
        title="Mtziri",
        pages=510,
        year=2024,
        seller_id=seller.id,
    )

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    response = await async_client.patch(
        f"{API_V1_URL_PREFIX}/{book.id}",
        json={"title": "Patched Title"},
    )

    assert response.status_code == status.HTTP_200_OK

    await db_session.refresh(book)
    assert book.title == "Patched Title"


@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="delete_seller@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        author="Lermontov",
        title="Mtziri",
        pages=510,
        year=2024,
        seller_id=seller.id,
    )

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="invalid_delete_seller@example.com",
        password="123456",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        author="Lermontov",
        title="Mtziri",
        pages=510,
        year=2024,
        seller_id=seller.id,
    )

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND