#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "psycopg2-binary>=2.9.0",
# ]
# ///
"""
PostgreSQL skill for Claude Code.

Provides database querying, CSV export, and schema exploration capabilities.
"""

import argparse
import csv
import os
import sys

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    sys.exit(1)


def get_connection():
    """
    Create database connection from environment variables.

    Returns:
        psycopg2 connection object

    Raises:
        ValueError: If required environment variables are missing
        psycopg2.Error: If connection fails
    """
    # Try connection string first
    conn_string = os.getenv("POSTGRES_URL")

    if conn_string:
        return psycopg2.connect(conn_string)

    # Fall back to individual parameters
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    if not all([database, user, password]):
        raise ValueError(
            "Missing required environment variables. "
            "Set POSTGRES_URL or (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)"
        )

    return psycopg2.connect(host=host, port=port, dbname=database, user=user, password=password)


def query_to_csv(*, sql_query: str, output_file: str) -> None:
    """
    Execute SQL query and export results to CSV.

    Args:
        sql_query: SQL query to execute
        output_file: Path to output CSV file

    Raises:
        psycopg2.Error: If query execution fails
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Execute query
        cursor.execute(sql_query)

        # Get column names
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]

            # Write to CSV
            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()

                # Stream results to avoid memory issues with large datasets
                for row in cursor:
                    writer.writerow(row)

        else:
            pass

    except psycopg2.Error:
        sys.exit(1)
    except Exception:
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def list_tables() -> None:
    """
    List all tables in the database (excluding system tables).
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT schemaname, tablename
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename
        """)

        tables = cursor.fetchall()

        if tables:
            for schema, table in tables:
                pass
        else:
            pass

    except psycopg2.Error:
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def describe_table(*, table_name: str) -> None:
    """
    Describe table structure (columns, types, nullable, defaults).

    Args:
        table_name: Name of table (can include schema: schema.table)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Parse schema and table
        if "." in table_name:
            schema, table = table_name.split(".", 1)
        else:
            schema = "public"
            table = table_name

        cursor.execute(
            """
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """,
            (schema, table),
        )

        columns = cursor.fetchall()

        if not columns:
            sys.exit(1)

        for col_name, data_type, max_length, nullable, default in columns:
            if max_length:
                pass

            str(default) if default else ""

    except psycopg2.Error:
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def list_schemas() -> None:
    """
    List all schemas in the database.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name
        """)

        schemas = cursor.fetchall()

        if schemas:
            for (schema,) in schemas:
                pass
        else:
            pass

    except psycopg2.Error:
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def main():
    """Main entry point for the skill."""
    parser = argparse.ArgumentParser(description="PostgreSQL database skill for Claude Code")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Query command
    query_parser = subparsers.add_parser("query", help="Execute SQL query and export to CSV")
    query_parser.add_argument("--sql", required=True, help="SQL query to execute")
    query_parser.add_argument("--output", required=True, help="Output CSV file path")

    # List tables command
    subparsers.add_parser("list-tables", help="List all tables in database")

    # Describe table command
    describe_parser = subparsers.add_parser("describe-table", help="Describe table structure")
    describe_parser.add_argument("--table", required=True, help="Table name (schema.table)")

    # List schemas command
    subparsers.add_parser("list-schemas", help="List all schemas in database")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == "query":
        query_to_csv(sql_query=args.sql, output_file=args.output)
    elif args.command == "list-tables":
        list_tables()
    elif args.command == "describe-table":
        describe_table(table_name=args.table)
    elif args.command == "list-schemas":
        list_schemas()


if __name__ == "__main__":
    main()
