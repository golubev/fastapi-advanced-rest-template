from sqlmodel import create_engine

from app.config import config

engine = create_engine(config.POSTGRES_URI, pool_pre_ping=True, echo=True)
