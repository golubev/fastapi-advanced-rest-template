from src.core.db import get_session
from src.services import todo_item_service


def update_status_overdue() -> int:
    with get_session() as db:
        todo_items_to_mark_as_overdue = todo_item_service.get_all_open_overdue(db)
        for todo_item in todo_items_to_mark_as_overdue:
            todo_item_service.mark_as_overdue(db, todo_item)
    return len(todo_items_to_mark_as_overdue)
