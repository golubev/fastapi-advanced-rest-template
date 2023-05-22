import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "prod"

    API_LIST_LIMIT_DEFAULT: int = 20

    TODO_ITEMS_DANGLING_HOURS_MAX: int = 24

    EMAIL_FROM_EMAIL: str
    EMAIL_FROM_NAME: str
    EMAIL_TEMPLATES_DIR: str = "./application/src/emails/templates/"

    SECURITY_SECRET_KEY: str = secrets.token_urlsafe(32)
    SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # 7 days

    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    RABBITMQ_HOST: str
    RABBITMQ_VIRTUAL_HOST: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    SMTP_DO_USE_TLS: bool
    SMTP_PORT: str
    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str

    class Config:
        case_sensitive = True

    def get_postgres_uri(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        )

    def get_rabbitmq_uri(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:5672/{self.RABBITMQ_VIRTUAL_HOST}"
        )


application_config = Settings()
