from database import Base, engine
from models import Users

class Repository:

    @staticmethod
    def create_tables():
        engine.echo = True
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)


Repository.create_tables()
