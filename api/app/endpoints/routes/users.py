from fastapi import APIRouter, status

from app.endpoints.dependencies import CurrentUserDependency, SessionDependency
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter()


@router.post("/users/", response_model=UserResponse)
def create_user(
    *,
    db: SessionDependency,
    create_api_model: UserCreate,
) -> User:
    """
    Register a new user.
    """
    return user_service.create(db, create_api_model)


@router.get("/users/current-user", response_model=UserResponse)
def read_current_user(
    *,
    current_user: CurrentUserDependency,
) -> User:
    """
    Get the current user's details.
    """
    return current_user


@router.put("/users/current-user", response_model=UserResponse)
def update_current_user(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
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
    db: SessionDependency,
    current_user: CurrentUserDependency,
) -> None:
    """
    Delete the current user.
    """
    user_service.delete(db, current_user)
