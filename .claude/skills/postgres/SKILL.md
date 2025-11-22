---
name: postgres
description: Query PostgreSQL databases, export results to CSV, list tables/schemas, and describe table structures. Use when needing to interact with PostgreSQL databases, run SQL queries, or export database data.
allowed-tools: Bash, Read, Write, Glob
---

# PostgreSQL Database Skill

Query PostgreSQL databases, export query results, and explore database schemas.

## Prerequisites

Required environment variables:
- `POSTGRES_HOST` - Database host (default: localhost)
- `POSTGRES_PORT` - Database port (default: 5432)
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password

Alternatively, use a connection string:
- `POSTGRES_URL` - Full connection string (e.g., `postgresql://user:pass@host:port/dbname`)

## Available Commands

### Query and Export

Run a SQL query and export results to CSV:

```bash
uv run .claude/skills/postgres/main.py query \
  --sql "SELECT * FROM table WHERE condition = true" \
  --output /tmp/results.csv
```

### List Tables

List all tables in the database:

```bash
uv run .claude/skills/postgres/main.py list-tables
```

### Describe Table

Show table structure (columns, types, constraints):

```bash
uv run .claude/skills/postgres/main.py describe-table --table table_name
```

### List Schemas

List all schemas in the database:

```bash
uv run .claude/skills/postgres/main.py list-schemas
```

## Usage Notes

- Script uses uv inline script metadata (PEP 723) - dependencies auto-installed on first run
- All queries use parameterized statements to prevent SQL injection
- CSV exports use UTF-8 encoding with proper escaping
- Read-only user recommended for monitoring/reporting use cases
- Large result sets are automatically streamed to avoid memory issues

## Error Handling

Common errors and solutions:

- **Connection refused**: Check host, port, and firewall settings
- **Authentication failed**: Verify username and password
- **Permission denied**: Ensure user has SELECT permission on target tables
- **Query timeout**: Add LIMIT clause or optimize query

## Security Considerations

- Never commit credentials to version control
- Use read-only database user when possible
- Parameterized queries prevent SQL injection
- Credentials are never logged or included in error messages
