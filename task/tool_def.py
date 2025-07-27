from commons.types import ToolResult, TextContent
from .service import get_task_service, Task, TaskPriority, TaskStatus


class TaskTool:
    """
    Unified task tool for all task operations.

    This class serves as the interface between the agent and the task management service.
    It defines the available actions (add, get, update, delete) and their respective
    parameters, translating high-level requests into concrete operations on tasks.
    """

    def __init__(self):
        """
        Initializes the TaskTool with its name, description, and parameter schema.

        The `parameters` attribute defines the expected input for this tool,
        allowing the agent to construct valid requests.
        """
        self.name = "task"
        self.description = "Comprehensive task management: add, get, update, delete tasks"
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "get", "update", "delete"],
                    "description": "The task management operation to perform"
                },
                "task_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of task IDs (for get/update/delete operations). Omit to get all tasks or delete all tasks."
                },
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name/description of the task"
                            },
                            "index": {
                                "type": "integer",
                                "description": "Position/order index (optional, defaults to end)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "normal"],
                                "description": "Task priority level (defaults to 'normal')"
                            }
                        },
                        "required": ["name"]
                    },
                    "description": "List of tasks to add (for add action)"
                },
                "update_type": {
                    "type": "string",
                    "enum": ["mark_done", "update_properties", "reorder"],
                    "description": "Type of update operation (for update action)"
                },
                "properties": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "normal"]}
                    },
                    "description": "Properties to update (for update action with update_properties type)"
                },
                "new_index": {
                    "type": "integer",
                    "description": "New index position (for update action with reorder type)"
                }
            },
            "required": ["action"]
        }

    def execute(self, params: dict) -> ToolResult:
        """
        Executes the specified task management operation based on the 'action' parameter.

        Args:
            params: A dictionary containing the parameters for the task operation,
                    as defined by the `self.parameters` schema.

        Returns:
            A ToolResult object indicating the outcome of the operation,
            including success or any errors encountered.
        """
        try:
            action = params.get("action")

            if action == "add":
                return self._add_tasks(params)
            elif action == "get":
                return self._get_tasks(params)
            elif action == "update":
                return self._update_tasks(params)
            elif action == "delete":
                return self._delete_tasks(params)
            else:
                return ToolResult(
                    content=[
                        TextContent(
                            type="text", text="Invalid action. Must be 'add', 'get', 'update', or 'delete'."
                        )
                    ],
                    isError=True
                )

        except Exception as e:
            return ToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True
            )

    def _add_tasks(self, params: dict) -> ToolResult:
        """
        Adds one or multiple tasks to the task service.

        Requires a 'tasks' array in the parameters, each containing at least a 'name'.

        Args:
            params: A dictionary minimally containing the 'tasks' key.

        Returns:
            ToolResult: Success message or an error if 'tasks' is missing.
        """
        tasks_data = params.get("tasks", [])
        if not tasks_data:
            return ToolResult(
                content=[TextContent(type="text", text="Tasks array is required for add action.")],
                isError=True
            )

        tasks = []
        for task_data in tasks_data:
            priority = TaskPriority.HIGH if task_data.get("priority") == "high" else TaskPriority.NORMAL
            index = task_data.get("index")
            task = Task(
                id=None,
                name=task_data["name"],
                index=index,
                status=TaskStatus.TODO,
                priority=priority
            )
            tasks.append(task)

        if len(tasks) == 1:
            get_task_service().append_task(tasks[0])
        else:
            get_task_service().append_tasks(tasks)

        task_count = len(tasks)
        task_word = "task" if task_count == 1 else "tasks"
        return ToolResult(
            content=[TextContent(type="text", text=f"Successfully added {task_count} {task_word}.")]
        )

    def _get_tasks(self, params: dict) -> ToolResult:
        """
        Retrieves specific tasks by ID or all tasks if no IDs are provided.

        Args:
            params: A dictionary optionally containing 'task_ids' to filter results.

        Returns:
            ToolResult: A message containing details of the found tasks or "No tasks found."
        """
        task_service = get_task_service()
        task_ids = params.get("task_ids")

        if task_ids is None:
            tasks = task_service.get_tasks()
        else:
            tasks = task_service.get_tasks_by_ids(task_ids)

        if not tasks:
            return ToolResult(
                content=[TextContent(type="text", text="No tasks found.")]
            )

        task_list = []
        for task in tasks:
            task_info = f"[{task.index}] {task.name} (ID: {task.id}, Status: {task.status.value}, Priority: {task.priority.value})"
            task_list.append(task_info)

        if len(tasks) == 1:
            result_text = f"Task: {task_list[0]}"
        else:
            result_text = f"Found {len(tasks)} tasks:\n" + "\n".join(task_list)

        return ToolResult(
            content=[TextContent(type="text", text=result_text)]
        )

    def _update_tasks(self, params: dict) -> ToolResult:
        """
        Updates tasks based on the specified 'update_type'.

        Dispatches to _mark_done, _update_properties, or _reorder_task.

        Args:
            params: A dictionary containing 'update_type' and other parameters
                    relevant to the specific update operation.

        Returns:
            ToolResult: Success message or an error if 'update_type' is invalid or missing.
        """
        task_service = get_task_service()
        update_type = params.get("update_type")
        task_ids = params.get("task_ids")

        if not update_type:
            return ToolResult(
                content=[TextContent(type="text", text="Value for update_type is required to run task update.")],
                isError=True
            )

        if update_type == "mark_done":
            return self._mark_done(task_service, task_ids)
        elif update_type == "update_properties":
            return self._update_properties(task_service, task_ids, params.get("properties", {}))
        elif update_type == "reorder":
            return self._reorder_task(task_service, task_ids, params.get("new_index"))
        else:
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Invalid update_type. Must be 'mark_done', 'update_properties', or 'reorder'."
                    )
                ],
                isError=True
            )

    def _delete_tasks(self, params: dict) -> ToolResult:
        """
        Deletes specific tasks by ID or all tasks if no IDs are provided.

        Args:
            params: A dictionary optionally containing 'task_ids' to specify which tasks to delete.

        Returns:
            ToolResult: Success message confirming deletion or indicating no tasks were found.
        """
        task_service = get_task_service()
        task_ids = params.get("task_ids")

        if task_ids is None:
            all_tasks = task_service.get_tasks()
            task_count = len(all_tasks)
            task_service.delete_all_tasks()
            return ToolResult(
                content=[TextContent(type="text", text=f"Successfully deleted all {task_count} tasks.")]
            )
        else:
            task_count = len(task_ids)
            task_service.delete_tasks(task_ids=task_ids)
            task_word = "task" if task_count == 1 else "tasks"
            return ToolResult(
                content=[TextContent(type="text", text=f"Successfully deleted {task_count} {task_word}.")]
            )

    def _mark_done(self, task_service, task_ids) -> ToolResult:
        """
        Marks tasks as done.

        If `task_ids` is None, all tasks will be marked as done.

        Args:
            task_service: The task service instance.
            task_ids: A list of task IDs to mark as done, or None for all tasks.

        Returns:
            ToolResult: Success message confirming the operation.
        """
        if task_ids is None:
            all_tasks = task_service.get_tasks()
            task_count = len(all_tasks)
            task_service.mark_all_tasks_as_done()
            return ToolResult(
                content=[TextContent(type="text", text=f"Successfully marked all {task_count} tasks as done.")]
            )
        else:
            task_count = len(task_ids)
            task_service.mark_multiple_tasks_as_done(task_ids)
            task_word = "task" if task_count == 1 else "tasks"
            return ToolResult(
                content=[TextContent(type="text", text=f"Successfully marked {task_count} {task_word} as done.")]
            )

    def _update_properties(self, task_service, task_ids, properties) -> ToolResult:
        """
        Updates properties (e.g., name, priority) for specified tasks.

        Requires `task_ids` and `properties` to be provided.

        Args:
            task_service: The task service instance.
            task_ids: A list of task IDs whose properties are to be updated.
            properties: A dictionary of properties to update (e.g., {"name": "New Name"}).

        Returns:
            ToolResult: Success message or an error if `task_ids` or `properties` are missing.
        """
        if not task_ids:
            return ToolResult(
                content=[TextContent(type="text", text="Task IDs are required for update_properties.")],
                isError=True
            )

        if not properties:
            return ToolResult(
                content=[TextContent(type="text", text="Properties are required for update_properties.")],
                isError=True
            )

        task_count = len(task_ids)
        for task_id in task_ids:
            task_service.update_task(task_id, **properties)

        task_word = "task" if task_count == 1 else "tasks"
        prop_names = list(properties.keys())
        return ToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Successfully updated {task_count} {task_word} ({', '.join(prop_names)})."
                )
            ]
        )

    def _reorder_task(self, task_service, task_ids, new_index) -> ToolResult:
        """
        Reorders a single task to a new index position.

        Requires exactly one task ID and a new_index.

        Args:
            task_service: The task service instance.
            task_ids: A list containing a single task ID to reorder.
            new_index: The new numerical index for the task.

        Returns:
            ToolResult: Success message or an error if requirements are not met.
        """
        if not task_ids or len(task_ids) != 1:
            return ToolResult(
                content=[TextContent(type="text", text="Exactly one task ID is required for reorder.")],
                isError=True
            )

        if new_index is None:
            return ToolResult(
                content=[TextContent(type="text", text="new_index is required for reorder.")],
                isError=True
            )

        task_id = task_ids[0]
        task_service.reorder_tasks(task_id, new_index)

        return ToolResult(
            content=[TextContent(type="text", text=f"Successfully reordered task to index {new_index}.")]
        )
