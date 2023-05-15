from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.config import config
from app.endpoints.dependencies.auth import get_current_user
from app.endpoints.dependencies.db import yield_session
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter()


@router.post("/users/current-user/tasks/")
def create_task(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
    create_api_model: TaskCreate,
) -> TaskResponse:
    """
    Create a new task.
    """
    task_db_model = task_service.create_for_user(db, create_api_model, current_user)
    return TaskResponse.from_db_model(task_db_model)


@router.get("/users/current-user/tasks/")
def list_tasks(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
    offset: int = 0,
    limit: int = config.API_LIST_LIMIT_DEFAULT,
) -> list[TaskResponse]:
    """
    List current user's tasks.
    """
    return [
        TaskResponse.from_db_model(task)
        for task in task_service.list_by_user(
            db, current_user, offset=offset, limit=limit
        )
    ]


@router.put("/users/current-user/tasks/{task_id}")
def update_task(
    *,
    db: Session = Depends(yield_session),
    current_user: User = Depends(get_current_user),
    task_id: int,
    update_api_model: TaskUpdate,
) -> TaskResponse:
    """
    Update current user's details.
    """
    task = task_service.get_or_exception(db, task_id)
    task_service.update_for_user(db, task, update_api_model, user=current_user)
    return TaskResponse.from_db_model(task)


@router.delete("/users/current-user/tasks/{task_id}")
def delete_task(
    *,
    db: Session = Depends(yield_session),
    task_id: int,
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Update current user's details.
    """
    task = task_service.get_or_exception(db, task_id)
    task_service.delete_for_user(db, task, user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
