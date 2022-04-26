import abc
from typing import List, Optional

import sqlalchemy

from adapters.orm import database
from domain.models import Book


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self, book_id) -> Optional[Book]:
        pass

    @abc.abstractmethod
    def add(self, book_id) -> None:
        pass

    @abc.abstractmethod
    def update(self, book_id: int, book: Book) -> bool:
        pass

    @abc.abstractmethod
    def list(self) -> List[Book]:
        pass

    @abc.abstractmethod
    def delete(self, book_id: int) -> bool:
        pass


class BookRepository(AbstractRepository):
    def __init__(self, table: sqlalchemy.Table) -> None:
        self.books = table

    async def get(self, book_id: int) -> Optional[Book]:
        query = self.books.select().where(self.books.c.id == book_id)
        return await database.fetch_one(query)

    async def add(self, book: Book) -> None:
        query = self.books.insert().values(tittle=book.tittle, author=book.author)
        await database.execute(query)

    async def update(self, book_id: int, book: Book) -> bool:
        current_book = await self.get(book_id)
        if current_book is None:
            return False
        query = (
            self.books.update()
            .where(self.books.c.id == book_id)
            .values(tittle=book.tittle, author=book.author)
        )
        await database.execute(query)
        return True

    async def list(self) -> List[Book]:
        query = self.books.select()
        return await database.fetch_all(query)

    async def delete(self, book_id: int) -> bool:
        current_book = await self.get(book_id)
        if current_book is None:
            return False
        query = self.books.delete().where(self.books.c.id == book_id)
        await database.execute(query)
        return True
