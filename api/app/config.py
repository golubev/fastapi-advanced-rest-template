import secrets

from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    SECURITY_SECRET_KEY: str = secrets.token_urlsafe(32)
    SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # 7 days

    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    API_LIST_LIMIT_DEFAULT = 20

    class Config:
        case_sensitive = True

    def get_postgres_uri(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"


config = Settings()
