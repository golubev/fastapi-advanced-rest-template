from datetime import datetime

from faker import Faker

from src.enums import TodoItemStatusEnum, TodoItemVisibilityEnum
from src.models import TodoItem, User


def make(
    faker: Faker,
    *,
    user: User,
    subject: str | None = None,
    deadline: datetime | None = None,
    status: TodoItemStatusEnum = TodoItemStatusEnum.OPEN,
    visibility: TodoItemVisibilityEnum | None = None,
    resolve_time: datetime | None = None,
) -> TodoItem:
    """
    Make a new fake `TodoItem` DB model without persisting it.

    :param user: `TodoItem.user` to set. A `TodoItem`'s owner
    :param subject: `TodoItem.subject` to set. Leave `None` to fake
    :param deadline: `TodoItem.deadline` to set. Is faked only when `None` passed \
    and status is `TodoItemStatusEnum.OVERDUE`
    :param status: `TodoItem.status` to set. Is not faked
    :param visibility: `TodoItem.visibility` to set. Leave `None` to fake
    :param resolve_time: `TodoItem.resolve_time` to set. Is faked only when `None` \
    passed and status is `TodoItemStatusEnum.RESOLVED`
    """
    if subject is None:
        subject = faker.unique.text(max_nb_chars=80)
    if deadline is None and status == TodoItemStatusEnum.OVERDUE:
        deadline = faker.past_datetime()
    if visibility is None:
        visibility = faker.enum(TodoItemVisibilityEnum)
    if resolve_time is None and status == TodoItemStatusEnum.RESOLVED:
        resolve_time = faker.past_datetime()
    return TodoItem(
        user=user,
        subject=subject,
        deadline=deadline,
        status=status,
        visibility=visibility,
        resolve_time=resolve_time,
    )
