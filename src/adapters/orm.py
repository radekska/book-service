import sqlalchemy

from settings import DATABASE_URL

metadata = sqlalchemy.MetaData()
books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("tittle", sqlalchemy.String),
    sqlalchemy.Column("author", sqlalchemy.String),
)
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
