from typing import List

import databases
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from starlette import status

from adapters.orm import books
from domain.schemas import BookIn, Book
from settings import DATABASE_URL

database = databases.Database(DATABASE_URL)
app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get(
    "/books/{book_id}",
    status_code=status.HTTP_200_OK,
    response_model=Book,
    responses={status.HTTP_404_NOT_FOUND: {"message": str}},
)
async def get_book(book_id: int):
    query = books.select().where(books.c.id == book_id)
    book = await database.fetch_one(query)
    return (
        book
        if book
        else JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "book not found"},
        )
    )


@app.post("/books", status_code=status.HTTP_201_CREATED, response_class=Response)
async def create_book(book: BookIn):
    query = books.insert().values(tittle=book.tittle, author=book.author)
    await database.execute(query)


@app.get("/books", response_model=List[Book])
async def get_books():
    query = books.select()
    return await database.fetch_all(query)


@app.put(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def update_book(book_id: int, book_in: BookIn):
    book = await database.fetch_one(books.select().where(books.c.id == book_id))
    if book is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "book not found"},
        )
    query = (
        books.update()
        .where(books.c.id == book_id)
        .values(tittle=book_in.tittle, author=book_in.author)
    )
    await database.execute(query)
