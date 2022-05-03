from typing import List

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from adapters.orm import mapper_registry
from adapters.repository import BookRepository
from database.session import async_session, engine
from domain.models import Book
from domain.schemas import BookIn, BookOut
from entrypoints.exceptions import BookNotFound
from settings import settings

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as connection:
        # await connection.run_sync(mapper_registry.metadata.drop_all)
        await connection.run_sync(mapper_registry.metadata.create_all)


async def get_db() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with async_session() as session:
        yield session
        await session.commit()


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK, response_model=BookOut)
async def get_book(
    book_id: int,
    authorize: AuthJWT = Depends(AuthJWT),
    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    book = await BookRepository(session).get_by_id(_id=book_id)
    if not book:
        raise BookNotFound(book_id=book_id)
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED, response_class=Response)
async def create_book(
    book_in: BookIn,
    authorize: AuthJWT = Depends(AuthJWT),
    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    await BookRepository(session).add(
        book=Book(tittle=book_in.tittle, author=book_in.author)
    )


@app.get("/books", status_code=status.HTTP_200_OK, response_model=List[BookOut])
async def get_books(
    authorize: AuthJWT = Depends(AuthJWT),
    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    return await BookRepository(session=session).list()


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
    is_updated = await BookRepository(session=session).update(
        book_id, book=Book(tittle=book_in.tittle, author=book_in.author)
    )
    if not is_updated:
        raise BookNotFound(book_id=book_id)


@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_book(book_id: int, authorize: AuthJWT = Depends(AuthJWT),    session: AsyncSession = Depends(get_db),
):
    authorize.jwt_required()
    is_deleted = await BookRepository(session=session).delete(_id=book_id)
    if not is_deleted:
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


@app.post("/login")
async def login(user: User, authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}
