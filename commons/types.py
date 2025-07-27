from pydantic import BaseModel


class TextContent(BaseModel):
    """
    Text content for tool results.

    Attributes:
        type (str): The type of content, defaults to "text".
        text (str): The actual text content.
    """
    type: str = "text"
    text: str


class ToolResult(BaseModel):
    """
    Tool execution result - same pattern as original MCP ToolResult.

    Represents the standardized output of a tool's execution, including
    its content and whether an error occurred.

    Attributes:
        content (list[TextContent]): A list of `TextContent` objects,
                                     which can contain textual results or error messages.
        isError (bool): A boolean indicating if the tool execution resulted in an error.
                        Defaults to False (no error).
    """
    content: list[TextContent]
    isError: bool = False
