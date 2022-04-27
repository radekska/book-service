from pydantic import BaseModel, Field


class BookIn(BaseModel):
    tittle: str = Field(max_length=191)
    author: str = Field(max_length=191)


class BookOut(BaseModel):
    id: int
    tittle: str = Field(max_length=191)
    author: str = Field(max_length=191)

