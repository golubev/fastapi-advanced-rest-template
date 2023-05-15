from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import AccessTokenException, AccessTokenPayload
from app.endpoints.dependencies.db import yield_session
from app.models import User
from app.services import user_service

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


def get_current_user(
    db: Session = Depends(yield_session), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        token_payload = AccessTokenPayload.decode_from_access_token(token)
    except AccessTokenException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return user_service.get_or_exception(db, id=int(token_payload.sub))
