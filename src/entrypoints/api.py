from typing import List

from fastapi import FastAPI
from fastapi.responses import Response
from starlette import status

from adapters.orm import books, database
from adapters.repository import BookRepository
from domain.models import Book
from domain.schemas import BookIn, BookOut
from entrypoints.exceptions import BookNotFound

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK, response_model=BookOut)
async def get_book(book_id: int):
    book = await BookRepository(table=books).get(book_id=book_id)
    if not book:
        raise BookNotFound(book_id=book_id)
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED, response_class=Response)
async def create_book(book: BookIn):
    book = Book(tittle=book.tittle, author=book.author)
    await BookRepository(table=books).add(book=book)


@app.get("/books", response_model=List[BookOut])
async def get_books():
    return await BookRepository(table=books).list()


#
#
@app.put(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def update_book(book_id: int, book: BookIn):
    is_updated = await BookRepository(table=books).update(book_id, book)
    if not is_updated:
        raise BookNotFound(book_id=book_id)
