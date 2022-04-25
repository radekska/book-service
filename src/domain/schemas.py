from pydantic import BaseModel


class BookIn(BaseModel):
    tittle: str
    author: str


class Book(BaseModel):
    id: int
    tittle: str
    author: str
