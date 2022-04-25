import http
import os
from typing import List

import databases
import sqlalchemy
from settings import DATABASE_URL
from fastapi import FastAPI
from pydantic import BaseModel

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()
books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("tittle", sqlalchemy.String),
    sqlalchemy.Column("author", sqlalchemy.String),
)
engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

app = FastAPI()


class BookIn(BaseModel):
    tittle: str
    author: str


class BookOut(BaseModel):
    id: int
    tittle: str
    author: str


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/books/{book_id}", response_model=BookOut)
async def get_book(book_id: int):
    query = books.select().where(books.c.id == book_id)
    return await database.fetch_one(query)


@app.post("/books/", status_code=http.HTTPStatus.CREATED)
async def create_book(book: BookIn):
    query = books.insert().values(tittle=book.tittle, author=book.author)
    book_id = await database.execute(query)
    return {"id": book_id}
