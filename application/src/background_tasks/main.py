from typing import Any

from celery import Celery

from src.core.email import send_email as core_send_email
from src.emails.todo_items import compose_overdue_email

from . import celeryconfig, tasks

application = Celery("background_tasks")
application.config_from_object(celeryconfig)


@application.task(acks_late=True)
def send_email(email_to: str, subject: str, body_html: str) -> None:
    core_send_email(email_to, subject, body_html)


@application.task(acks_late=True)
def todo_items_update_status_overdue() -> int:
    todo_items_marked_as_overdue = tasks.todo_items.update_status_overdue()

    for todo_item in todo_items_marked_as_overdue:
        send_email.apply_async(
            args=(todo_item.user.email, *compose_overdue_email(todo_item))
        )

    return len(todo_items_marked_as_overdue)


@application.task(acks_late=True)
def todo_items_move_dangling_to_archive() -> int:
    todo_items_moved_to_archive = tasks.todo_items.move_dangling_to_archive()
    return len(todo_items_moved_to_archive)


@application.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs: Any) -> None:
    sender.add_periodic_task(
        300,
        todo_items_update_status_overdue.s(),
        expires=240,
    )
    sender.add_periodic_task(
        300,
        todo_items_move_dangling_to_archive.s(),
        expires=240,
    )
