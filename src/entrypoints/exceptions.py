from fastapi import HTTPException
from starlette import status


class BookNotFound(HTTPException):
    def __init__(self, book_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id: '{book_id}' not found",
        )
