from fastapi import APIRouter, status

from src.api.dependencies import CurrentUserDependency, SessionDependency
from src.background_tasks import send_email
from src.emails.users import compose_registration_email
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
    new_user = user_service.create(db, create_api_model)

    send_email.apply_async(args=(new_user.email, *compose_registration_email(new_user)))

    return new_user


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
