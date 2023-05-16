from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.endpoints.dependencies.auth import get_current_user
from app.endpoints.dependencies.db import yield_session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter()


@router.post("/users/")
def create_user(
    *,
    db: Session = Depends(yield_session),
    create_api_model: UserCreate,
) -> UserResponse:
    """
    Register a new user.
    """
    user_db_model = user_service.create(db, create_api_model)
    return UserResponse.from_db_model(user_db_model)


@router.get("/users/current-user")
def read_current_user(
    *,
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get the current user's details.
    """
    return UserResponse.from_db_model(current_user)


@router.put("/users/current-user")
def update_current_user(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
    update_api_model: UserUpdate,
) -> UserResponse:
    """
    Update the current user's details.
    """
    user_service.update(db, current_user, update_api_model)
    return UserResponse.from_db_model(current_user)


@router.delete("/users/current-user")
def delete_current_user(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Delete the current user.
    """
    user_service.delete(db, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
