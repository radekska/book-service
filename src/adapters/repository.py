import abc
from typing import Optional, Iterable

from domain.models import Book
from domain.schemas import BookOut
from pydantic import BaseModel
from sqlalchemy import update, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class AbstractRepository(abc.ABC):
    session: AsyncSession

    @property
    @abc.abstractmethod
    def _schema(self) -> BaseModel:
        pass

    @property
    @abc.abstractmethod
    def _model(self):
        pass

    async def get_by_id(self, _id: int) -> Optional[BaseModel]:
        entry = await self.session.execute(
            select(self._model).where(self._model.id == _id)
        )
        try:
            entry = entry.scalar_one()
        except NoResultFound:
            return
        return self._schema.from_orm(entry)


class BookRepository(AbstractRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @property
    def _schema(self) -> BookOut:
        return BookOut

    @property
    def _model(self) -> Book:
        return Book

    async def add(self, book: Book) -> None:
        self.session.add(book)
        await self.session.commit()

    async def update(self, _id: int, book: Book) -> bool:
        current_book = await self.get_by_id(_id)
        if not current_book:
            return False
        await self.session.execute(
            update(self._model)
                .where(self._model.id == _id)
                .values(tittle=book.tittle, author=book.author)
        )
        return True

    async def list(self) -> Iterable[BookOut]:
        books = await self.session.execute(select(self._model))
        return (self._schema.from_orm(book) for book in books.scalars())

    async def delete(self, _id: int) -> bool:
        current_book = await self.get_by_id(_id)
        if current_book is None:
            return False
        await self.session.execute(delete(self._model).where(self._model.id == _id))
        return True
