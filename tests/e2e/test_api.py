import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from adapters.repository import SQLAlchemyBookRepository
from domain.models import Book
from domain.schemas import BookOut

pytestmark = pytest.mark.asyncio


async def test_book_create(
    authed_async_client: AsyncClient, db_session: AsyncSession
) -> None:
    book_repository = SQLAlchemyBookRepository(session=db_session)
    payload = {
        "tittle": "How to buy Twitter",
        "author": "Elon Musk",
    }
    response = await authed_async_client.post(url="/books", json=payload)
    books = await book_repository.list()

    assert response.status_code == status.HTTP_201_CREATED
    assert tuple(books) == (
        BookOut(id=1, tittle="How to buy Twitter", author="Elon Musk"),
    )


async def test_book_retrieve(
    authed_async_client: AsyncClient, db_session: AsyncSession
) -> None:
    await SQLAlchemyBookRepository(session=db_session).create(
        book=Book(tittle="Performance over Horizon", author="John Doe")
    )

    response = await authed_async_client.get(url="/books/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "author": "John Doe",
        "tittle": "Performance over Horizon",
    }


async def test_books_retrieve(
    authed_async_client: AsyncClient, db_session: AsyncSession
) -> None:
    await SQLAlchemyBookRepository(session=db_session).create(
        book=Book(tittle="Performance over Horizon", author="John Doe")
    )
    await SQLAlchemyBookRepository(session=db_session).create(
        book=Book(tittle="Python Pro", author="Jane Doe")
    )

    response = await authed_async_client.get(url="/books")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"author": "John Doe", "id": 1, "tittle": "Performance over Horizon"},
        {"author": "Jane Doe", "id": 2, "tittle": "Python Pro"},
    ]


async def test_book_update(
    authed_async_client: AsyncClient, db_session: AsyncSession
) -> None:
    repository = SQLAlchemyBookRepository(session=db_session)
    await repository.create(
        Book(tittle="Microservices security in action", author="Joe Doe")
    )

    payload = {"tittle": "Microservices security in action", "author": "Dias"}
    response = await authed_async_client.put(url="/books/1", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await repository.get_by_id(_id=1) == BookOut(
        id=1, tittle="Microservices security in action", author="Dias"
    )


async def test_book_delete(
    authed_async_client: AsyncClient, db_session: AsyncSession
) -> None:
    repository = SQLAlchemyBookRepository(session=db_session)
    await repository.create(
        Book(tittle="Microservices security in action", author="Joe Doe")
    )

    response = await authed_async_client.delete(url="/books/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    books = await repository.list()
    assert len(tuple(books)) == 0


@pytest.mark.parametrize(
    "method, payload",
    (("GET", {}), ("PUT", {"tittle": "T", "author": "A"}), ("DELETE", {})),
)
async def test_book_not_found(
    method: str, payload: dict, authed_async_client: AsyncClient
) -> None:
    response = await authed_async_client.request(
        method=method, url="/books/150", json=payload
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Book with id: '150' not found"}


@pytest.mark.parametrize(
    "method, payload, url",
    (
        ("GET", {}, "/books/9"),
        ("GET", {}, "/books"),
        ("POST", {"tittle": "F", "author": "D"}, "/books"),
        ("PUT", {"tittle": "T", "author": "A"}, "/books/5"),
        ("DELETE", {}, "/books/5"),
    ),
)
async def test_jwt_authentication_no_header(
    method: str, payload: dict, url: str, async_client: AsyncClient
) -> None:
    response = await async_client.request(method=method, url=url, json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Missing Authorization Header"}


async def test_dummy_retrieve_token(async_client: AsyncClient) -> None:
    response = await async_client.post(
        url="/token", json={"username": "test", "password": "test"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


async def test_dummy_retrieve_token_invalid_credentials(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        url="/token", json={"username": "john-doe", "password": "super-secret"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Bad username or password"}
