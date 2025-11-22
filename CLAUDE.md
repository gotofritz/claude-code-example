# Project Info

- Issue tracker: GitHub Issues
- Repository: Use `gh` CLI for all GitHub operations

## Development Standards

**Start here:** README.md for purpose, docs/project-plan.md for current state

## Code

- Every important file has a docstring at the top explaining its purpose
- Type hints on all function signatures. Use native types when possible, i.e. `list` and not `List`
- Use pydantic for data models
- All imports root-relative and at the top of the file
- All commands should be run from the project root
- At the start of a session run source .venv/bin/activate
- Organise work in small, atomic commits
- At the end of a big set of changes, run `poe qa`
- Limit linting exceptions. If you have to, add a comment explaining why you think you have to.

## Python

- Tools: uv, ruff, mypy, pytest
- CLI: click
- Enforce named arguments for functions with >1 parameter
- Testing: pytest with faker, polyfactory, pytest-data

## Enforcement

- Pre-commit: ruff, mypy
- CI: full test suite
