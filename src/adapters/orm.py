from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import registry

from domain.models import Book

mapper_registry = registry()

books = Table(
    "books",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("tittle", String(191)),
    Column("author", String(191)),
)

mapper_registry.map_imperatively(Book, books)
