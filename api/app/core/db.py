from sqlalchemy import create_engine

from app.config import config

engine = create_engine(config.get_postgres_uri(), pool_pre_ping=True, echo=True)
