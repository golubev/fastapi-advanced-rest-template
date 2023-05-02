from sqlmodel import create_engine, SQLModel, Session

from app.config import config

engine = create_engine(config.POSTGRES_URI, pool_pre_ping=True, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
