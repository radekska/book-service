from typing import List

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from adapters.orm import mapper_registry
from adapters.repository import SQLAlchemyBookRepository
from database.session import engine, get_db
from domain.models import Book
from domain.schemas import BookIn, BookOut
from entrypoints.exceptions import BookNotFound
from service_layer.services import (
    get,
    BookNotFoundInRepository,
    create,
    get_many,
    update,
    delete,
)
from settings import settings

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as connection:
        # await connection.run_sync(mapper_registry.metadata.drop_all)
        await connection.run_sync(mapper_registry.metadata.create_all)


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK, response_model=BookOut)
async def get_book(
    book_id: int,
    authorize: AuthJWT = Depends(AuthJWT),
    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    try:
        book = await get(
            book_id=book_id, repository=SQLAlchemyBookRepository(session)
        )
        return book
    except BookNotFoundInRepository:
        raise BookNotFound(book_id=book_id)


@app.post("/books", status_code=status.HTTP_201_CREATED, response_class=Response)
async def create_book(
    book_in: BookIn,
    authorize: AuthJWT = Depends(AuthJWT),
    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    await create(
        book=Book(tittle=book_in.tittle, author=book_in.author),
        repository=SQLAlchemyBookRepository(session=session),
    )


@app.get("/books", status_code=status.HTTP_200_OK, response_model=List[BookOut])
async def get_books(
    authorize: AuthJWT = Depends(AuthJWT),
    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    return await get_many(repository=SQLAlchemyBookRepository(session=session))


@app.put(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def update_book(
    book_id: int,
    book_in: BookIn,
    authorize: AuthJWT = Depends(AuthJWT),
    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    try:
        await update(
            book_id=book_id,
            book=Book(tittle=book_in.tittle, author=book_in.author),
            repository=SQLAlchemyBookRepository(session=session),
        )
    except BookNotFoundInRepository:
        raise BookNotFound(book_id=book_id)


@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_book(
    book_id: int,
    authorize: AuthJWT = Depends(AuthJWT),
    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    try:
        await delete(
            book_id=book_id, repository=SQLAlchemyBookRepository(session=session)
        )
    except BookNotFoundInRepository:
        raise BookNotFound(book_id=book_id)


@AuthJWT.load_config
def get_config():
    return settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exception: AuthJWTException):
    return JSONResponse(
        status_code=exception.status_code, content={"detail": exception.message}
    )


class User(BaseModel):
    username: str
    password: str


@app.post("/token")
async def login(user: User, authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}
