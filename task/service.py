from .types import Task, TaskPriority, TaskStatus


class TaskService:
    """
    Manages a collection of tasks, providing functionalities to add, retrieve, update, and delete them.

    Tasks are identified by unique IDs and can be ordered using numerical indices.
    The service handles automatic ID and index assignment to prevent conflicts
    and provides methods for common task operations like marking as done,
    prioritizing, and reordering.
    """

    def __init__(self):
        """Initializes the TaskService with an empty task collection and a counter for generating unique task IDs."""
        self.tasks: dict[str, Task] = {}
        self._task_counter = 1

    def _get_next_index(self) -> int:
        """
        Determines the next available index for a new task.

        If tasks exist, it returns the maximum current index plus one.
        Otherwise, it returns 0 for the first task.
        """
        if not self.tasks:
            return 0
        return max(task.index for task in self.tasks.values()) + 1

    def _get_next_task_id(self) -> str:
        """Generates a unique, auto-incrementing task ID."""
        task_id = f"task_{self._task_counter}"
        self._task_counter += 1
        return task_id

    def append_task(self, task: Task) -> None:
        """
        Appends a single task to the collection.

        Automatically assigns a unique ID and an incremental index if not provided.
        Raises ValueError if the task ID or index already exists.

        Args:
            task: The Task object to be added.
        """
        # Auto-assign ID if not provided
        if not task.id:
            task.id = self._get_next_task_id()
        elif task.id in self.tasks:
            raise ValueError(f"Task ID {task.id} already exists.")

        # Auto-assign index if not provided
        if task.index is None:
            task.index = self._get_next_index()
        else:
            # Check for duplicate index if one was provided
            for t in self.tasks.values():
                if t.index == task.index:
                    raise ValueError(f"Index {task.index} is already in use.")

        self.tasks[task.id] = task

    def append_tasks(self, tasks: list[Task]) -> None:
        """
        Appends multiple tasks to the collection in a batch.

        Ensures all tasks have unique IDs and indices, assigning them automatically
        if not provided. Validates against existing tasks and duplicates within
        the incoming list to prevent conflicts.

        Args:
            tasks: A list of Task objects to be added.

        Raises:
            ValueError: If any task ID or index conflicts with existing tasks
                        or other tasks in the input list.
        """
        existing_ids = {task_id for task_id in self.tasks.keys()}
        existing_indices = {task.index for task in self.tasks.values()}

        incoming_ids = set()
        incoming_indices = set()
        next_auto_index = self._get_next_index()

        # First pass: validate and assign IDs and indices
        for i, task in enumerate(tasks):
            # Auto-assign ID if not provided
            if not task.id:
                task.id = self._get_next_task_id()
            else:
                # Check for duplicate ID in existing tasks
                if task.id in existing_ids:
                    raise ValueError(f"Task with ID {task.id} already exists.")
                # Check for duplicate ID within the incoming batch itself
                if task.id in incoming_ids:
                    raise ValueError(f"Duplicate task ID {task.id} found in the input list.")

            # Auto-assign index if not provided
            if task.index is None:
                task.index = next_auto_index + i
            else:
                # Check for duplicate index in existing tasks
                if task.index in existing_indices:
                    raise ValueError(f"Index {task.index} is already in use.")
                # Check for duplicate index within the incoming batch itself
                if task.index in incoming_indices:
                    raise ValueError(f"Duplicate task index {task.index} found in the input list.")

            # Add to sets for future checks within the same batch
            incoming_ids.add(task.id)
            incoming_indices.add(task.index)

        # Second pass: add all of em
        for task in tasks:
            self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Task:
        """
        Retrieves a specific task by its unique ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The Task object corresponding to the given ID.

        Raises:
            KeyError: If no task with the specified ID is found.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with ID {task_id} not found.")
        return self.tasks[task_id]

    def get_tasks(self) -> list[Task]:
        """
        Retrieves all tasks currently managed by the service.

        The tasks are returned sorted by their numerical index in ascending order.
        """
        return sorted(list(self.tasks.values()), key=lambda t: t.index)

    def get_tasks_by_ids(self, task_ids: list[str]) -> list[Task]:
        """
        Retrieves a list of tasks specified by their IDs.

        Tasks are returned sorted by their numerical index.

        Args:
            task_ids: A list of task IDs to retrieve.

        Returns:
            A list of Task objects corresponding to the given IDs.

        Raises:
            KeyError: If any task with a specified ID is not found.
        """
        tasks = []
        for task_id in task_ids:
            if task_id not in self.tasks:
                raise KeyError(f"Task with ID {task_id} not found.")
            tasks.append(self.tasks[task_id])
        return sorted(tasks, key=lambda t: t.index)

    def mark_task_as_done(self, task_id: str) -> None:
        """
        Updates the status of a single task to 'DONE'.

        Args:
            task_id: The ID of the task to mark as done.

        Raises:
            KeyError: If no task with the specified ID is found.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with ID {task_id} not found.")
        self.tasks[task_id].status = TaskStatus.DONE

    def mark_multiple_tasks_as_done(self, task_ids: list[str]) -> None:
        """
        Marks multiple tasks as done in a batch operation.

        Ensures all specified tasks exist before proceeding with any status updates.

        Args:
            task_ids: A list of task IDs to mark as done.

        Raises:
            KeyError: If any of the specified task IDs are not found.
        """
        # First, check if all tasks exist before marking any changes
        for task_id in task_ids:
            if task_id not in self.tasks:
                raise KeyError(f"Task with ID {task_id} not found. Cannot mark all tasks as done.")

        # If all checks pass, proceed with marking
        for task_id in task_ids:
            self.mark_task_as_done(task_id=task_id)

    def mark_all_tasks_as_done(self) -> None:
        """Marks all tasks currently in the service as 'DONE'."""
        for task_id in self.tasks:
            self.mark_task_as_done(task_id=task_id)

    def update_task(self, task_id: str, **kwargs) -> None:
        """
        Updates one or more properties of a specific task.

        Supported properties can be passed as keyword arguments (e.g., `name="New Name"`).
        Handles conversion for `priority` if a string value is provided.

        Args:
            task_id: The ID of the task to update.
            **kwargs: Keyword arguments where the key is the property name and the value is the new value.

        Raises:
            KeyError: If no task with the specified ID is found.
            AttributeError: If an attempt is made to update a property that does not exist on the Task object.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with ID {task_id} not found.")
        task = self.tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                # Convert priority string to enum if needed
                if key == "priority" and isinstance(value, str):
                    value = TaskPriority.HIGH if value == "high" else TaskPriority.NORMAL
                setattr(task, key, value)
            else:
                raise AttributeError(f"Task object has no attribute '{key}' to update.")

    def prioritize_task(self, task_id: str, new_priority: TaskPriority) -> None:
        """
        Sets the priority level for a specific task.

        Args:
            task_id: The ID of the task to prioritize.
            new_priority: The new priority level (e.g., `TaskPriority.HIGH`, `TaskPriority.NORMAL`).

        Raises:
            KeyError: If no task with the specified ID is found.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with ID {task_id} not found.")
        self.tasks[task_id].priority = new_priority

    def reorder_tasks(self, task_id: str, new_index: int) -> None:
        """
        Reorders a task by swapping its index with another task at the target index.

        This method effectively swaps the positions of two tasks. If the `task_id`'s
        current index is already `new_index`, no action is taken.

        Args:
            task_id: The ID of the task to reorder.
            new_index: The target index where the task should be moved.

        Raises:
            KeyError: If the task with `task_id` is not found.
            ValueError: If no task is found at the `new_index`.
        """
        curr_task = self.tasks.get(task_id)
        if not curr_task:
            raise KeyError(f"Task with ID {task_id} not found.")

        target_task = None
        for task in self.tasks.values():
            if task.index == new_index:
                target_task = task
                break

        if not target_task:
            raise ValueError(f"No task found with target index {new_index}.")

        if curr_task == target_task:
            return

        original_curr_index = curr_task.index
        curr_task.index = target_task.index
        target_task.index = original_curr_index

    def delete_task(self, task_id: str) -> None:
        """
        Deletes a single task from the collection by its ID.

        Args:
            task_id: The ID of the task to delete.

        Raises:
            KeyError: If no task with the specified ID is found.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with ID {task_id} not found.")
        del self.tasks[task_id]

    def delete_tasks(self, task_ids: list[str]) -> None:
        """
        Deletes multiple tasks from the collection in a batch.

        Ensures all specified tasks exist before proceeding with any deletions.

        Args:
            task_ids: A list of task IDs to delete.

        Raises:
            KeyError: If any of the specified task IDs are not found.
        """
        # Check if all tasks exist before deleting any
        for task_id in task_ids:
            if task_id not in self.tasks:
                raise KeyError(f"Task with ID {task_id} not found. Cannot perform batch deletion.")

        # If all checks pass, proceed with deletion
        for task_id in task_ids:
            self.delete_task(task_id=task_id)

    def delete_all_tasks(self) -> None:
        """Delete all tasks currently managed by the service."""
        self.tasks.clear()


_task_service = None


def get_task_service() -> TaskService:
    """
    Provides a singleton instance of TaskService.

    This function ensures that only one instance of TaskService is created
    and used throughout the application, promoting consistent task management.
    """
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
