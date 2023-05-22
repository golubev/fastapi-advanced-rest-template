from src.config import application_config
from src.core.db import get_session
from src.services import todo_item_service


def update_status_overdue() -> int:
    with get_session() as db:
        todo_items_to_mark_as_overdue = todo_item_service.get_all_open_overdue(db)
        for todo_item in todo_items_to_mark_as_overdue:
            todo_item_service.mark_as_overdue(db, todo_item)
    return len(todo_items_to_mark_as_overdue)


def move_dangling_to_archive() -> int:
    with get_session() as db:
        todo_items_to_move_to_archive = (
            todo_item_service.get_all_visible_not_open_dangling(
                db,
                hours_in_status=application_config.TODO_ITEMS_DANGLING_HOURS_MAX,
            )
        )
        for todo_item in todo_items_to_move_to_archive:
            todo_item_service.move_to_archive(db, todo_item)
    return len(todo_items_to_move_to_archive)
