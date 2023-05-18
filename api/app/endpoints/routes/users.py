from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.endpoints.dependencies.auth import get_current_user
from app.endpoints.dependencies.db import yield_session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter()


@router.post("/users/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(yield_session),
    create_api_model: UserCreate,
) -> User:
    """
    Register a new user.
    """
    return user_service.create(db, create_api_model)


@router.get("/users/current-user", response_model=UserResponse)
def read_current_user(
    *,
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current user's details.
    """
    return current_user


@router.put("/users/current-user", response_model=UserResponse)
def update_current_user(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
    update_api_model: UserUpdate,
) -> User:
    """
    Update the current user's details.
    """
    user_service.update(db, current_user, update_api_model)
    return current_user


@router.delete(
    "/users/current-user",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_current_user(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete the current user.
    """
    user_service.delete(db, current_user)
