import abc
from typing import List, Optional

from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.orm import Books
from domain.models import Book
from domain.schemas import BookOut


class AbstractRepository(abc.ABC):
    @property
    @abc.abstractmethod
    def _table(self):
        pass

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
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @property
    def _table(self) -> Table:
        return Books

    async def get(self, book_id: int) -> Optional[BookOut]:
        entry = await self.session.get(self._table, book_id)
        return BookOut.from_orm(entry)

    async def add(self, book: Book) -> None:
        entry = self._table(**book.dict())
        self.session.add(entry)
        await self.session.commit()

    async def update(self, book_id: int, book: Book) -> bool:
        pass
        # current_book = await self.get(book_id)
        # if current_book is None:
        #     return False
        # query = (
        #     self._table.update()
        #         .where(self._table.c.id == book_id)
        #         .values(tittle=book.tittle, author=book.author)
        # )
        # await database.execute(query)
        # return True

    async def list(self) -> List[Book]:
        pass
        # query = self._table.select()
        # return await database.fetch_all(query)

    async def delete(self, book_id: int) -> bool:
        pass
        # current_book = await self.get(book_id)
        # if current_book is None:
        #     return False
        # query = self._table.delete().where(self._table.c.id == book_id)
        # await database.execute(query)
        # return True
