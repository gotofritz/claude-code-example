# PostgreSQL Skill

Query PostgreSQL databases, export results to CSV, and explore database schemas.

## Installation

Add the required dependency to your project:

```bash
uv add psycopg2-binary
```

## Configuration

Set environment variables for database connection:

```bash
# Option 1: Connection string
export POSTGRES_URL="postgresql://user:password@host:port/database"

# Option 2: Individual parameters
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="your_database"
export POSTGRES_USER="your_user"
export POSTGRES_PASSWORD="your_password"
```

For local development, add these to a `.env` file (ensure it's gitignored).

## Usage

### Query and Export to CSV

```bash
python3 .claude/skills/postgres/main.py query \
  --sql "SELECT * FROM users WHERE created_at > '2024-01-01'" \
  --output /tmp/recent_users.csv
```

### List All Tables

```bash
python3 .claude/skills/postgres/main.py list-tables
```

### Describe Table Structure

```bash
python3 .claude/skills/postgres/main.py describe-table --table users
# Or with schema:
python3 .claude/skills/postgres/main.py describe-table --table public.users
```

### List All Schemas

```bash
python3 .claude/skills/postgres/main.py list-schemas
```

## Security Best Practices

- **Never commit credentials** to version control
- Use **read-only database user** for monitoring/reporting
- Use **environment variables** or secrets management (1Password CLI, AWS Secrets Manager)
- All queries use **parameterized statements** to prevent SQL injection
- Credentials are **never logged** or included in error messages

## Example: Using with Claude Code

When Claude Code invokes this skill, it can:

1. Query database for specific conditions
2. Export results to CSV
3. Analyze the data
4. Use results in other skills (e.g., send via Slack)

Example prompt:
```
Check the database for any users created in the last 24 hours and export to CSV
```

Claude will automatically:
- Construct appropriate SQL query
- Run the postgres skill with query command
- Export results to temporary CSV
- Report findings

## Troubleshooting

### Connection Refused
- Check `POSTGRES_HOST` and `POSTGRES_PORT`
- Verify database is running
- Check firewall/security group rules

### Authentication Failed
- Verify `POSTGRES_USER` and `POSTGRES_PASSWORD`
- Check user exists in database
- Ensure password is correctly escaped in connection string

### Permission Denied
- Ensure user has `SELECT` permission on target tables
- Check schema permissions
- Consider using a read-only user for safety

### Query Timeout
- Add `LIMIT` clause to reduce result size
- Optimize query with indexes
- Consider pagination for large datasets
