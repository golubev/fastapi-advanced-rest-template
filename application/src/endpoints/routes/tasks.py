from fastapi import APIRouter, status

from src.config import config
from src.endpoints.dependencies import CurrentUserDependency, SessionDependency
from src.enums import TaskVisibilityEnum
from src.models import Task
from src.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.services import task_service

router = APIRouter()


@router.post("/users/current-user/tasks/", response_model=TaskResponse)
def create_task(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    create_api_model: TaskCreate,
) -> Task:
    """
    Create a new task.
    """
    return task_service.create_for_user(db, create_api_model, current_user)


@router.get("/users/current-user/tasks/", response_model=list[TaskResponse])
def list_tasks(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    visibility: TaskVisibilityEnum | None = None,
    offset: int = 0,
    limit: int = config.API_LIST_LIMIT_DEFAULT,
) -> list[Task]:
    """
    List current user's tasks.
    """
    return task_service.list_by_user(
        db,
        current_user,
        visibility=visibility,
        offset=offset,
        limit=limit,
    )


@router.put("/users/current-user/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    task_id: int,
    update_api_model: TaskUpdate,
) -> Task:
    """
    Update a task.
    """
    task = task_service.get_for_user_or_exception(db, task_id, current_user)
    task_service.update(db, task, update_api_model)
    return task


@router.post("/users/current-user/tasks/{task_id}/resolve", response_model=TaskResponse)
def resolve_task(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    task_id: int,
) -> Task:
    """
    Transfer an open task into resolved state.
    """
    task = task_service.get_for_user_or_exception(db, task_id, current_user)
    task_service.resolve(db, task)
    return task


@router.post("/users/current-user/tasks/{task_id}/reopen", response_model=TaskResponse)
def reopen_task(
    *,
    db: SessionDependency,
    current_user: CurrentUserDependency,
    task_id: int,
) -> Task:
    """
    Reopen a resolved task.
    """
    task = task_service.get_for_user_or_exception(db, task_id, current_user)
    task_service.reopen(db, task)
    return task


@router.delete(
    "/users/current-user/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    *,
    db: SessionDependency,
    task_id: int,
    current_user: CurrentUserDependency,
) -> None:
    """
    Delete a task.
    """
    task = task_service.get_for_user_or_exception(db, task_id, current_user)
    task_service.delete(db, task)
