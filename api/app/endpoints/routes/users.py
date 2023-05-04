from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.endpoints.dependencies.auth import get_current_user
from app.endpoints.dependencies.db import get_session
from app.endpoints.validators import (
    validate_user_email_not_exists,
    validate_user_username_not_exists,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter()


@router.post("/users/")
def create_user(
    *,
    db: Session = Depends(get_session),
    create_api_model: UserCreate,
) -> UserRead:
    """
    Register a new user.
    """
    validate_user_email_not_exists(create_api_model.email, db)
    validate_user_username_not_exists(create_api_model.username, db)
    return user_service.create(db, create_api_model=create_api_model)


@router.get("/users/current-user")
def read_current_user(
    *,
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Get current user.
    """
    return UserRead.from_model(current_user)


@router.put("/users/current-user")
def update_current_user(
    *,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    update_api_model: UserUpdate,
) -> UserRead:
    """
    Update current user's details.
    """
    if update_api_model.username != current_user.username:
        validate_user_username_not_exists(update_api_model.username, db)
    user = user_service.update(
        db, db_model=current_user, data_to_update=update_api_model
    )
    return user
