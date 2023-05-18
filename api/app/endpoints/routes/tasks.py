from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import config
from app.endpoints.dependencies.auth import get_current_user
from app.endpoints.dependencies.db import yield_session
from app.enums import TaskVisibilityEnum
from app.models import Task, User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter()


@router.post("/users/current-user/tasks/", response_model=TaskResponse)
def create_task(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
    create_api_model: TaskCreate,
) -> Task:
    """
    Create a new task.
    """
    return task_service.create_for_user(db, create_api_model, current_user)


@router.get("/users/current-user/tasks/", response_model=list[TaskResponse])
def list_tasks(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
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
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
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
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
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
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
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
    db: Session = Depends(yield_session),
    task_id: int,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a task.
    """
    task = task_service.get_for_user_or_exception(db, task_id, current_user)
    task_service.delete(db, task)
