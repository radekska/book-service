import databases
import sqlalchemy

from settings import settings

metadata = sqlalchemy.MetaData()
books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("tittle", sqlalchemy.String),
    sqlalchemy.Column("author", sqlalchemy.String),
)
engine = sqlalchemy.create_engine(settings.database_url)
metadata.create_all(engine)

database = databases.Database(settings.database_url)
