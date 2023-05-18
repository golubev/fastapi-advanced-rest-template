from datetime import datetime

from faker import Faker

from app.enums import TaskStatusEnum, TaskVisibilityEnum
from app.models import Task, User


def make(
    faker: Faker,
    *,
    user: User,
    subject: str | None = None,
    deadline: datetime | None = None,
    status: TaskStatusEnum = TaskStatusEnum.OPEN,
    visibility: TaskVisibilityEnum | None = None,
    resolve_time: datetime | None = None,
) -> Task:
    """
    Make a new fake `Task` DB model without persisting it.

    :param user: `Task.user` to set. The task's owner
    :param subject: `Task.subject` to set. Leave `None` to fake
    :param deadline: `Task.deadline` to set. Is faked only when `None` passed \
    and status is `TaskStatusEnum.OVERDUE`
    :param status: `Task.status` to set. Is not faked
    :param visibility: `Task.visibility` to set. Leave `None` to fake
    :param resolve_time: `Task.resolve_time` to set. Is faked only when `None` passed \
    and status is `TaskStatusEnum.RESOLVED`
    """
    if subject is None:
        subject = faker.unique.text(max_nb_chars=80)
    if deadline is None and status == TaskStatusEnum.OVERDUE:
        deadline = faker.past_datetime()
    if visibility is None:
        visibility = faker.enum(TaskVisibilityEnum)
    if resolve_time is None and status == TaskStatusEnum.RESOLVED:
        resolve_time = faker.past_datetime()
    return Task(
        user=user,
        subject=subject,
        deadline=deadline,
        status=status,
        visibility=visibility,
        resolve_time=resolve_time,
    )
