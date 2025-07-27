# LLM Tools

A collection of framework-agnostic tools for LLM integrations. Each tool is designed to be easily integrated into AI agents, MCP servers, or other applications.

> **Battle-tested**: Every tool here was originally developed for and used in my AI agent. They've been extracted, cleaned up, and made framework-agnostic so you can use them in your own projects.

## Available Tools

### 📋 [Task](task/)
Complete CRUD task management with priorities, status tracking, and auto-assignment.
- In-memory state for session-based usage
- Framework-agnostic design
- Comprehensive test coverage
- [Full Documentation](task/README.md)

## Installation

```bash
# Development
git clone https://github.com/kamillobinski/llm-tools.git
cd llm-tools
pip install -e .

# Production
pip install llm-tools

# With development dependencies
pip install -e ".[dev]"
```

## Project Structure

```
llm-tools/
├── commons/         # Shared types and utilities
├── task/            # Task management tool
│   ├── README.md    # Tool documentation
│   └── tests/       # Test suite
└── pyproject.toml   # Package configuration
```

## Requirements

- Python 3.8+
- pydantic

## Contributing

1. Install: `pip install -e ".[dev]"`
2. Test: `pytest`
3. Add tests for new features

## License

MIT License