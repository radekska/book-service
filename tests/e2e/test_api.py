import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from adapters.repository import BookRepository
from domain.models import Book
from domain.schemas import BookOut

pytestmark = pytest.mark.asyncio


async def test_book_create(
    authed_async_client: AsyncClient, db_session: AsyncSession
) -> None:
    book_repository = BookRepository(session=db_session)
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
    await BookRepository(session=db_session).add(
        book=Book(tittle="Performance over Horizon", author="John Doe")
    )

    response = await authed_async_client.get(url="/books/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "author": "John Doe",
        "tittle": "Performance over Horizon",
    }
