from src.core.email import compose_email
from src.models import TodoItem


def compose_overdue_email(todo_item: TodoItem) -> tuple[str, str]:
    return compose_email(
        '"{{ todo_item.subject }}" has passed the deadline',
        "todo_item_overdue.html",
        {
            "todo_item": todo_item,
        },
    )
