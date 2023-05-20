from fastapi import APIRouter, status

from src.api.dependencies import CurrentUserDependency, SessionDependency
from src.config import config
from src.enums import TodoItemVisibilityEnum
from src.models import TodoItem
from src.schemas.todo_item import TodoItemCreate, TodoItemResponse, TodoItemUpdate
from src.services import todo_item_service

router = APIRouter()


@router.post("/users/current-user/todo_items/", response_model=TodoItemResponse)
def create_todo_item(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    create_api_model: TodoItemCreate,
) -> TodoItem:
    """
    Create a new `TodoItem`
    """
    return todo_item_service.create_for_user(db, create_api_model, current_user)


@router.get("/users/current-user/todo_items/", response_model=list[TodoItemResponse])
def list_todo_items(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    visibility: TodoItemVisibilityEnum | None = None,
    offset: int = 0,
    limit: int = config.API_LIST_LIMIT_DEFAULT,
) -> list[TodoItem]:
    """
    List current user's `TodoItems`
    """
    return todo_item_service.list_by_user(
        db,
        current_user,
        visibility=visibility,
        offset=offset,
        limit=limit,
    )


@router.put(
    "/users/current-user/todo_items/{todo_item_id}", response_model=TodoItemResponse
)
def update_todo_item(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    todo_item_id: int,
    update_api_model: TodoItemUpdate,
) -> TodoItem:
    """
    Update a `TodoItem`
    """
    todo_item = todo_item_service.get_for_user_or_exception(
        db, todo_item_id, current_user
    )
    todo_item_service.update(db, todo_item, update_api_model)
    return todo_item


@router.post(
    "/users/current-user/todo_items/{todo_item_id}/resolve",
    response_model=TodoItemResponse,
)
def resolve_todo_item(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    todo_item_id: int,
) -> TodoItem:
    """
    Transfer an open `TodoItem` into resolved state
    """
    todo_item = todo_item_service.get_for_user_or_exception(
        db, todo_item_id, current_user
    )
    todo_item_service.resolve(db, todo_item)
    return todo_item


@router.post(
    "/users/current-user/todo_items/{todo_item_id}/reopen",
    response_model=TodoItemResponse,
)
def reopen_todo_item(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    todo_item_id: int,
) -> TodoItem:
    """
    Reopen a resolved `TodoItem`
    """
    todo_item = todo_item_service.get_for_user_or_exception(
        db, todo_item_id, current_user
    )
    todo_item_service.reopen(db, todo_item)
    return todo_item


@router.delete(
    "/users/current-user/todo_items/{todo_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_todo_item(
    *,
    db: SessionDependency,
    todo_item_id: int,
    current_user: CurrentUserDependency,
) -> None:
    """
    Delete a `TodoItem`
    """
    todo_item = todo_item_service.get_for_user_or_exception(
        db, todo_item_id, current_user
    )
    todo_item_service.delete(db, todo_item)
