from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.endpoints.dependencies.db import get_session
from app.schemas.token import TokenResponse
from app.services import user_service

router = APIRouter()


@router.post("/login/access-token")
def login_for_access_token(
    db: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()
) -> TokenResponse:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_service.get_db_model_by_credentials_verified(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    return TokenResponse(access_token=create_access_token(user.id), token_type="bearer")
