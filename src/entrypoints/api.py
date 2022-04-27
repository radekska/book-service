from typing import List

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from starlette import status

from adapters.orm import books, database
from adapters.repository import BookRepository
from domain.models import Book
from domain.schemas import BookIn, BookOut
from entrypoints.exceptions import BookNotFound
from settings import settings

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK, response_model=BookOut)
async def get_book(book_id: int, authorize: AuthJWT = Depends(AuthJWT)):
    authorize.jwt_required()
    book = await BookRepository(table=books).get(book_id=book_id)
    if not book:
        raise BookNotFound(book_id=book_id)
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED, response_class=Response)
async def create_book(book: BookIn, authorize: AuthJWT = Depends(AuthJWT)):
    authorize.jwt_required()
    book = Book(tittle=book.tittle, author=book.author)
    await BookRepository(table=books).add(book=book)


@app.get("/books", status_code=status.HTTP_200_OK, response_model=List[BookOut])
async def get_books(authorize: AuthJWT = Depends(AuthJWT)):
    authorize.jwt_required()
    return await BookRepository(table=books).list()


@app.put(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def update_book(book_id: int, book: BookIn, authorize: AuthJWT = Depends(AuthJWT)):
    authorize.jwt_required()
    is_updated = await BookRepository(table=books).update(book_id, book)
    if not is_updated:
        raise BookNotFound(book_id=book_id)


@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_book(book_id: int, authorize: AuthJWT = Depends(AuthJWT)):
    authorize.jwt_required()
    is_deleted = await BookRepository(table=books).delete(book_id=book_id)
    if not is_deleted:
        raise BookNotFound(book_id=book_id)


@AuthJWT.load_config
def get_config():
    return settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exception: AuthJWTException):
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": exception.message}
    )


class User(BaseModel):
    username: str
    password: str


@app.post('/login')
async def login(user: User, authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}
