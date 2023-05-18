from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.security import AccessTokenPayload
from app.endpoints.dependencies import SessionDependency
from app.models import User
from app.services import user_service

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


def get_current_user(
    db: SessionDependency,
    token: Annotated[str, Depends(reusable_oauth2)],
) -> User:
    token_payload = AccessTokenPayload.decode_from_access_token(token)
    return user_service.get_or_exception(db, id=int(token_payload.sub))


CurrentUserDependency = Annotated[User, Depends(get_current_user)]
