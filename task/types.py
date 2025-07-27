from enum import Enum

from pydantic import BaseModel


class TaskPriority(Enum):
    """Task priority values."""
    HIGH = "high"
    NORMAL = "normal"


class TaskStatus(Enum):
    """Task status values."""
    TODO = "todo"
    DONE = "done"


class Task(BaseModel):
    """
    Task model.

    Represents a single task with its unique identifier, name, order,
    status, and priority.

    Attributes:
        id (str | None):  A unique identifier for the task. Can be None for auto-assignment.
        name (str): The name or description of the task.
        index (int | None): The numerical index representing the task's position/order.
                            Defaults to None, meaning it can be ordered at the end.
        status (TaskStatus): The current completion status of the task.
                             Defaults to TaskStatus.TODO.
        priority (TaskPriority): The urgency level of the task.
                                 Defaults to TaskPriority.NORMAL.
    """
    id: str | None = None
    name: str
    index: int | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.NORMAL
