from datetime import datetime

from sqlalchemy.orm import Session

from src.enums import TodoItemStatusEnum, TodoItemVisibilityEnum
from src.models import TodoItem, User
from src.schemas.todo_item import TodoItemCreate, TodoItemUpdate

from .base_service import BaseService
from .exceptions import (
    OwnerAccessViolationException,
    StateConflictException,
    ValidationException,
)


class TodoItemService(BaseService[TodoItem]):
    def get_for_user(self, db: Session, id: int, user_owner: User) -> TodoItem | None:
        """
        Get a `TodoItem` by `id`. Check if the `user_owner` is an owner of the \
        `TodoItem`.
        """
        todo_item = self._get(db, id)
        if todo_item is None:
            return None
        self._check_is_owner(todo_item, user_owner)
        return todo_item

    def get_for_user_or_exception(
        self, db: Session, id: int, user_owner: User
    ) -> TodoItem:
        """
        Get a `TodoItem` by `id`. Raise exception if not found. Check if the \
        `user_owner` is an owner of the `TodoItem`.
        """
        todo_item = self._get_or_exception(db, id)
        self._check_is_owner(todo_item, user_owner)
        return todo_item

    def list_by_user(
        self,
        db: Session,
        user: User,
        *,
        visibility: TodoItemVisibilityEnum | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[TodoItem]:
        query = db.query(TodoItem).filter(TodoItem.user_id == user.id)
        if visibility is not None:
            query = query.filter(TodoItem.visibility == visibility)
        return query.offset(offset).limit(limit).all()

    def create_for_user(
        self, db: Session, create_api_model: TodoItemCreate, user: User
    ) -> TodoItem:
        """
        Create a new `TodoItem` with a given `user` as owner.
        """
        data_to_create_prepared = dict(
            **create_api_model.dict(),
            user_id=user.id,
        )
        return self._create(db, data_to_create_prepared)

    def update(
        self,
        db: Session,
        db_model: TodoItem,
        update_api_model: TodoItemUpdate,
    ) -> None:
        if db_model.status == TodoItemStatusEnum.OPEN:
            if (
                update_api_model.deadline is not None
                and update_api_model.deadline < datetime.now()
            ):
                raise ValidationException("deadline can not be set in the past")
        data_to_update_prepared = update_api_model.dict()
        self._update(db, db_model, data_to_update_prepared)

    def resolve(self, db: Session, db_model: TodoItem) -> None:
        if db_model.status != TodoItemStatusEnum.OPEN:
            raise StateConflictException(
                f"Can resolve TodoItems only in status"
                f" '{TodoItemStatusEnum.OPEN.value}'"
            )
        data_to_update_prepared = {
            "status": TodoItemStatusEnum.RESOLVED,
            "resolve_time": datetime.now(),
        }
        self._update(db, db_model, data_to_update_prepared)

    def reopen(self, db: Session, db_model: TodoItem) -> None:
        if db_model.status != TodoItemStatusEnum.RESOLVED:
            raise StateConflictException(
                f"Can reopen TodoItems only in status"
                f" '{TodoItemStatusEnum.RESOLVED.value}'"
            )
        data_to_update_prepared = {
            "status": TodoItemStatusEnum.OPEN,
            "resolve_time": None,
        }
        self._update(db, db_model, data_to_update_prepared)

    def delete(self, db: Session, db_model: TodoItem) -> None:
        self._delete(db, db_model)

    def _check_is_owner(self, db_model: TodoItem, user: User) -> None:
        if db_model.user_id != user.id:
            raise OwnerAccessViolationException(
                "Only a TodoItem's owner user may have access to it"
            )


todo_item_service = TodoItemService(TodoItem)
