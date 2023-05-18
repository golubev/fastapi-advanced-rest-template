from enum import Enum


class TaskStatusEnum(Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    OVERDUE = "overdue"
