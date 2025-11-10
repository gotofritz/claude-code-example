# Development Standards

**Start here:** README.md for purpose, claude/project-plan.md for current state

## Code

- Every important file has a docstring at the top explaining its purpose
- Type hints on all function signatures
- Use pydantic for data models

## Python

- Tools: uv, ruff, mypy, pytest
- CLI: click
- Enforce named arguments for functions with >1 parameter
- Testing: pytest with faker, polyfactory, pytest-data

## Enforcement

- Pre-commit: ruff, mypy
- CI: full test suite
