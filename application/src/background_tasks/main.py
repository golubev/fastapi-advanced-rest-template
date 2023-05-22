from typing import Any

from celery import Celery

from . import celeryconfig, tasks

application = Celery("background_tasks")
application.config_from_object(celeryconfig)


@application.task(acks_late=True)
def todo_items_update_status_overdue() -> int:
    return tasks.todo_items.update_status_overdue()


@application.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs: Any) -> None:
    sender.add_periodic_task(
        60,
        todo_items_update_status_overdue.s(),
        expires=40,
    )
