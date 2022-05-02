from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Books(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    tittle = Column(String, nullable=False)
    author = Column(String, nullable=False)
