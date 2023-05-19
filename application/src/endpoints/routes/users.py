from fastapi import APIRouter, status

from src.endpoints.dependencies import CurrentUserDependency, SessionDependency
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse, UserUpdate
from src.services import user_service

router = APIRouter()


@router.post("/users/", response_model=UserResponse)
def create_user(
    *,
    db: SessionDependency,
    create_api_model: UserCreate,
) -> User:
    """
    Register (create) a new `User`.
    """
    return user_service.create(db, create_api_model)


@router.get("/users/current-user", response_model=UserResponse)
def read_current_user(
    *,
    current_user: CurrentUserDependency,
) -> User:
    """
    Get the current (authenticated) `User`'s details.
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
    Update the current (authenticated) `User`'s details.
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
    Delete the current (authenticated) `User`.
    """
    user_service.delete(db, current_user)
