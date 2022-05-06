from typing import Iterable

from adapters.repository import AbstractRepository
from domain.models import Book


class BookNotFoundInRepository(Exception):
    def __init__(self, book_id: int) -> None:
        super().__init__(f"Book with identifier '{book_id}' not found in repository")


async def create(book: Book, repository: AbstractRepository) -> None:
    await repository.create(book=book)


async def get(book_id: int, repository: AbstractRepository) -> Book:
    book = await repository.get_by_id(_id=book_id)
    if book is None:
        raise BookNotFoundInRepository(book_id=book_id)
    return book


async def get_many(repository: AbstractRepository) -> Iterable[Book]:
    return await repository.list()


async def update(book_id: int, book: Book, repository: AbstractRepository) -> None:
    is_updated = await repository.update(_id=book_id, book=book)
    if not is_updated:
        raise BookNotFoundInRepository(book_id=book_id)


async def delete(book_id: int, repository: AbstractRepository) -> None:
    is_deleted = await repository.delete(_id=book_id)
    if not is_deleted:
        raise BookNotFoundInRepository(book_id=book_id)
