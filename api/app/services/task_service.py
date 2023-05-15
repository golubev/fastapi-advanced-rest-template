from typing import Any

from sqlalchemy.orm import Session

from app.models import Task, User
from app.schemas.task import TaskCreate, TaskUpdate

from .base_service import BaseService
from .exceptions import OwnerAccessViolationException


class TaskService(BaseService[Task, TaskCreate, TaskUpdate]):
    def create_for_user(
        self, db: Session, data_to_create: TaskCreate | dict[str, Any], user: User
    ) -> Task:
        """
        Create a new task related to a given user.
        """
        if isinstance(data_to_create, dict):
            data_to_create = TaskCreate(**data_to_create)
        data_to_create_prepared = dict(
            **data_to_create.dict(),
            user_id=user.id,
        )
        return self.create(db, data_to_create_prepared)

    def list_by_user(
        self, db: Session, user: User, *, offset: int = 0, limit: int = 100
    ) -> list[Task]:
        """
        List user's tasks.
        """
        return (
            db.query(Task)
            .filter(Task.user_id == user.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_for_user(
        self,
        db: Session,
        db_model: Task,
        data_to_update: TaskUpdate | dict[str, Any],
        user: User,
    ) -> None:
        """
        Update a task of a given user.
        """
        self._check_is_owner(db, db_model, user)
        if isinstance(data_to_update, dict):
            # perform pydantic validations
            data_to_update = TaskUpdate(**data_to_update)
        self.update(db, db_model, data_to_update)

    def delete_for_user(self, db: Session, db_model: Task, user: User) -> None:
        """
        Delete a task for a given user
        """
        self._check_is_owner(db, db_model, user)
        self.delete(db, db_model)

    def _check_is_owner(self, db: Session, db_model: Task, user: User) -> None:
        if db_model.user_id != user.id:
            raise OwnerAccessViolationException(
                "Access forbidden as the user is not an owner"
            )


task_service = TaskService(Task)
