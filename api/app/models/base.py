from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseDBModel(Base):
    __abstract__ = True
