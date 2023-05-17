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
    visibility: TaskVisibilityEnum | None = TaskVisibilityEnum.VISIBLE,
    resolve_time: datetime | None = None,
) -> Task:
    """
    Make a new fake `Task` DB model without persisting it.

    :param user: `Task.user` to set. The task's owner
    :param subject: `Task.subject` to set. Leave `None` to generate a fake value
    :param deadline: `Task.deadline` to set. Is not faked
    :param status: `Task.status` to set. Is not faked
    :param visibility: `Task.visibility` to set. Leave `None` to generate a fake value
    :param resolve_time: `Task.resolve_time` to set. Is not faked
    """
    if subject is None:
        subject = faker.unique.text(max_nb_chars=80)
    # if isinstance(deadline, bool) and deadline:
    #     deadline = faker.future_datetime()
    if visibility is None:
        visibility = faker.enum(TaskVisibilityEnum)
    return Task(
        user=user,
        subject=subject,
        deadline=deadline,
        status=status,
        visibility=visibility,
        resolve_time=resolve_time,
    )
