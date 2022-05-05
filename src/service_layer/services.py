from sqlalchemy.ext.asyncio import AsyncSession

from adapters.repository import AbstractRepository
from domain.models import Book


class BookNotFoundInRepository(Exception):
    def __init__(self, book_id: int) -> None:
        super().__init__(f"Book with identifier '{book_id}' not found in repository")


def update(book: Book, repository: AbstractRepository):
    pass


async def add(book: Book, repository: AbstractRepository) -> None:
    await repository.add(book=book)


async def get(book_id: int, repository: AbstractRepository) -> Book:
    book = await repository.get_by_id(_id=book_id)
    if book is None:
        raise BookNotFoundInRepository
    return book


def many():
    pass
