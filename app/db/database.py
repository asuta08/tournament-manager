from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.db.config import DATABASE_URL

engine = create_engine(
    url=DATABASE_URL,
    connect_args={"connect_timeout": 5}
)

session_factory = sessionmaker(engine)

class Base(DeclarativeBase):
    pass