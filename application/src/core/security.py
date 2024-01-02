from datetime import UTC, datetime, timedelta
from typing import Self

import bcrypt
from jose import jwt
from jose.exceptions import JWTError
from pydantic import BaseModel, ValidationError

from src.config import application_config
from src.core.exceptions import AccessTokenMalformedException

ALGORITHM = "HS256"


class AccessTokenPayload(BaseModel):
    sub: str
    exp: datetime

    @classmethod
    def decode_from_access_token(cls, token: str) -> Self:
        try:
            payload = jwt.decode(
                token, application_config.SECURITY_SECRET_KEY, algorithms=[ALGORITHM]
            )
            return cls(**payload)
        except (JWTError, ValidationError):
            raise AccessTokenMalformedException("Could not validate credentials")

    def encode_to_access_token(self) -> str:
        return jwt.encode(
            self.dict(), key=application_config.SECURITY_SECRET_KEY, algorithm=ALGORITHM
        )


def generate_access_token(subject: int | str) -> str:
    expire = datetime.now(UTC) + timedelta(
        seconds=application_config.SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS
    )
    token_payload = AccessTokenPayload(sub=str(subject), exp=expire)
    return token_payload.encode_to_access_token()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
