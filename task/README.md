# Task Management Tool

A lean, mean task management tool. It's a logic ripped right out of me agent and ready to roll in your system or MCP server.

> **💡 Perfect as Built-in Agent Tool**: This tool uses in-memory state management, making it ideal as a built-in tool for AI agents during conversation sessions. It's designed for session-based task tracking, not persistent cross-session storage.

## Features

- **Full CRUD**: Add, grab, update, nuke. All the basics.
- **Flexible**: Priorities, status, custom order.
- **No Baggage**: Doesn't care about your MCP setup.
- **Auto-Magic**: IDs and indexes handle themselves.
- **Batch Mode**: Do a bunch at once, no sweat.
- **Type Safe**: Pydantic's got its back.
- **Clean Outputs**: `ToolResult` objects, not some messy dict.

## Quick Start

### Service Usage

```python
from task import TaskService, Task, TaskPriority, TaskStatus

# Spin up the service
service = TaskService()

# Drop a task in (ID gets made automatically)
task = Task(name="Finish the damn docs", priority=TaskPriority.HIGH)
service.append_task(task)

# See what's cooking
tasks = service.get_tasks()
print(f"Total tasks: {len(tasks)}")

# Mark it done, move on
service.mark_task_as_done(task.id)
```

### Tool Usage

```python
from task import TaskTool, ToolResult, TextContent

# Make your tool
tool = TaskTool()

# Add a couple tasks
result = tool.execute({
    "action": "add",
    "tasks": [
        {"name": "Write unit tests", "priority": "high"},
        {"name": "Update documentation", "priority": "normal"}
    ]
})

# What you get back is a ToolResult
print(result.content[0].text)  # "Successfully added 2 tasks."
print(result.isError)          # False

# Get everything
result = tool.execute({"action": "get"})
print(result.content[0].text)  # Task details
```

## Integration Examples

### FastMCP Integration

```python
# For MCP servers using fastmcp
from fastmcp import FastMCP
from task import TaskTool

mcp = FastMCP("Task Manager")
task_tool = TaskTool()

@mcp.tool()
async def task_manager(
    action: str,
    task_ids: list[str] = None,
    tasks: list[dict] = None,
    update_type: str = None,
    properties: dict = None,
    new_index: int = None
) -> str:
    """Task management tool"""
    params = {
        "action": action,
        "task_ids": task_ids,
        "tasks": tasks,
        "update_type": update_type,
        "properties": properties,
        "new_index": new_index
    }
    # Clean out the empty spots
    params = {k: v for k, v in params.items() if v is not None}
    
    result = task_tool.execute(params)
    return result.content[0].text
```

### Custom MCP Integration

```python
from task import TaskTool, ToolResult

class MCPTaskIntegration:
    def __init__(self):
        self.task_tool = TaskTool()
    
    def get_tool_definition(self) -> dict:
        """Sends back the MCP tool definition"""
        return {
            "type": "function",
            "function": {
                "name": self.task_tool.name,
                "description": self.task_tool.description,
                "parameters": self.task_tool.parameters
            }
        }
    
    async def execute(self, params: dict) -> dict:
        """Runs the task management operation"""
        result = self.task_tool.execute(params)
        
        # Convert to MCP format - use model_dump() instead of manual unpacking
        return {
            "content": [content.model_dump() for content in result.content],
            "isError": result.isError
        }
```

> **MCP Tool Schema Format**: Don't forget the standard MCP tool schema requires:
> ```python
> {
>     "type": "function",
>     "function": {
>         "name": "tool_name",
>         "description": "tool description", 
>         "parameters": { /* JSON schema */ }
>     }
> }
> ```

## API Reference

### TaskService

The brain of the operation.

**Methods:**

- `append_task(task: Task)` - Adds a single task
- `append_tasks(tasks: list[Task])` - Adds many
- `get_task(task_id: str) -> Task` - Grabs one by ID
- `get_tasks() -> list[Task]` - Grabs all of 'em, sorted
- `get_tasks_by_ids(task_ids: list[str]) -> list[Task]` - Grabs specific ones
- `mark_task_as_done(task_id: str)` - Marks one as done by ID
- `mark_multiple_tasks_as_done(task_ids: list[str])` - Marks multiple as done
- `mark_all_tasks_as_done()` - Marks all of 'em as done
- `update_task(task_id: str, **kwargs)` - Updates task properties
- `prioritize_task(task_id: str, new_priority: TaskPriority)` - Sets task priority
- `reorder_tasks(task_id: str, new_index: int)` - Reorders task position
- `delete_task(task_id: str)` - Deletes a task
- `delete_tasks(task_ids: list[str])` - Deletes a bunch
- `delete_all_tasks()` - Clear the slate

### TaskTool

The standard interface.

**Properties:**

- `name: str` - Tool name ("task")
- `description: str` - Tool description
- `parameters: dict` - JSON schema for parameters

**Methods:**

- `execute(params: dict) -> ToolResult` - Run it

### Data Models

#### Task

```python
class Task(BaseModel):
    id: str | None = None                     # Unique ID (auto-assigned if null)
    name: str                                 # What you call it
    index: int | None = None                  # Order (auto-assigned if null)
    status: TaskStatus = TaskStatus.TODO      # Current state
    priority: TaskPriority = TaskPriority.NORMAL  # Urgency level
```

#### Response Models

```python
class ToolResult(BaseModel):
    content: list[TextContent]                # The goods
    isError: bool = False                     # Did it break?

class TextContent(BaseModel):
    type: str = "text"                        # Always "text" here
    text: str                                 # The message
```

#### Enums

```python
class TaskStatus(Enum):
    TODO = "todo"
    DONE = "done"

class TaskPriority(Enum):
    HIGH = "high"
    NORMAL = "normal"
```

## Tool Parameters

### Required

- `action`: `"add"` | `"get"` | `"update"` | `"delete"`

### Optional (based on action)

- `task_ids`: List of task IDs (for get/update/delete)
- `tasks`: List of task objects (for add)
  - `name`: string (required)
  - `index`: integer (optional)
  - `priority`: `"high"` | `"normal"` (optional)
- `update_type`: `"mark_done"` | `"update_properties"` | `"reorder"` (for update)
- `properties`: Object with properties to update (for `update_properties`)
- `new_index`: Integer for new position (for `reorder`)

## Usage Examples

### Adding Tasks

```python
result = tool.execute({
    "action": "add",
    "tasks": [
        {"name": "Task 1", "priority": "high"},
        {"name": "Task 2", "index": 0}
    ]
})
```

### Getting Tasks

```python
# All of them
result = tool.execute({"action": "get"})

# Specific ones
result = tool.execute({
    "action": "get",
    "task_ids": ["task_1", "task_2"]
})
```

### Updating Tasks

```python
# Mark them done
result = tool.execute({
    "action": "update",
    "update_type": "mark_done",
    "task_ids": ["task_1"]
})

# Change properties
result = tool.execute({
    "action": "update",
    "update_type": "update_properties", 
    "task_ids": ["task_1"],
    "properties": {"name": "Updated task name", "priority": "high"}
})

# Reorder a task
result = tool.execute({
    "action": "update",
    "update_type": "reorder",
    "task_ids": ["task_1"],
    "new_index": 2
})
```

### Deleting Tasks

```python
# Specific ones
result = tool.execute({
    "action": "delete",
    "task_ids": ["task_1", "task_2"]
})

# All tasks
result = tool.execute({"action": "delete"})
```

## Response Format

Every tool operation returns a `ToolResult` object:

```python
class ToolResult(BaseModel):
    content: list[TextContent]  # The response
    isError: bool = False       # Set to True if something went wrong

class TextContent(BaseModel):
    type: str = "text"          # Always text
    text: str                   # What actually happened
```

### Success Example

```python
ToolResult(
    content=[TextContent(type="text", text="Successfully added 1 task.")],
    isError=False
)
```

### Error Example

```python
ToolResult(
    content=[TextContent(type="text", text="Error: Task ID test already exists")],
    isError=True
)
```

## Requirements

- Python 3.8+
- pydantic