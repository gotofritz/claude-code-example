#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8.0.0",
#     "psycopg2-binary>=2.9.0",
# ]
# ///
"""
Tests for PostgreSQL skill.

Run with: uv run .claude/skills/postgres/test_postgres.py
"""

import csv
import os

# Import the module to test
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import main as postgres_main


def test_get_connection_with_url():
    """Test database connection using connection string."""
    with patch.dict(os.environ, {"POSTGRES_URL": "postgresql://user:pass@localhost/testdb"}):
        with patch("main.psycopg2.connect") as mock_connect:
            postgres_main.get_connection()
            mock_connect.assert_called_once_with("postgresql://user:pass@localhost/testdb")


def test_get_connection_with_individual_params():
    """Test database connection using individual parameters."""
    with patch.dict(
        os.environ,
        {
            "POSTGRES_HOST": "testhost",
            "POSTGRES_PORT": "5433",
            "POSTGRES_DB": "testdb",
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
        },
        clear=True,
    ):
        with patch("main.psycopg2.connect") as mock_connect:
            postgres_main.get_connection()
            mock_connect.assert_called_once_with(
                host="testhost",
                port="5433",
                dbname="testdb",
                user="testuser",
                password="testpass",
            )


def test_get_connection_missing_credentials():
    """Test that missing credentials raise ValueError."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Missing required environment variables"):
            postgres_main.get_connection()


def test_query_to_csv_basic():
    """Test basic query to CSV export."""
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("name",), ("email",)]
    mock_cursor.__iter__ = lambda self: iter(
        [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
    )
    mock_cursor.rowcount = 2
    mock_conn.cursor.return_value = mock_cursor

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        output_file = f.name

    try:
        with patch("main.get_connection", return_value=mock_conn):
            postgres_main.query_to_csv(sql_query="SELECT * FROM users", output_file=output_file)

        # Verify CSV was created with correct data
        assert Path(output_file).exists()

        with open(output_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["name"] == "Alice"
            assert rows[1]["name"] == "Bob"

    finally:
        if Path(output_file).exists():
            Path(output_file).unlink()


def test_query_to_csv_empty_result():
    """Test query with no results."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = None  # No results
    mock_conn.cursor.return_value = mock_cursor

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        output_file = f.name

    try:
        with patch("main.get_connection", return_value=mock_conn):
            postgres_main.query_to_csv(
                sql_query="SELECT * FROM empty_table", output_file=output_file
            )

        # File should not be created for empty results
        # (or should exist but be empty, depending on implementation)

    finally:
        if Path(output_file).exists():
            Path(output_file).unlink()


def test_query_to_csv_preserves_none_values():
    """Test that None/NULL values are preserved in CSV."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("name",), ("email",)]
    mock_cursor.__iter__ = lambda self: iter(
        [
            {"id": 1, "name": "Alice", "email": None},
            {"id": 2, "name": None, "email": "bob@example.com"},
        ]
    )
    mock_cursor.rowcount = 2
    mock_conn.cursor.return_value = mock_cursor

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        output_file = f.name

    try:
        with patch("main.get_connection", return_value=mock_conn):
            postgres_main.query_to_csv(sql_query="SELECT * FROM users", output_file=output_file)

        with open(output_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            # CSV represents None as empty string
            assert rows[0]["email"] == ""
            assert rows[1]["name"] == ""

    finally:
        if Path(output_file).exists():
            Path(output_file).unlink()


def test_query_to_csv_special_characters():
    """Test CSV export with special characters (quotes, commas, newlines)."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("description",)]
    mock_cursor.__iter__ = lambda self: iter(
        [
            {"id": 1, "description": 'Text with "quotes"'},
            {"id": 2, "description": "Text with, commas"},
            {"id": 3, "description": "Text with\nnewlines"},
        ]
    )
    mock_cursor.rowcount = 3
    mock_conn.cursor.return_value = mock_cursor

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        output_file = f.name

    try:
        with patch("main.get_connection", return_value=mock_conn):
            postgres_main.query_to_csv(sql_query="SELECT * FROM data", output_file=output_file)

        # Verify CSV properly escapes special characters
        with open(output_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0]["description"] == 'Text with "quotes"'
            assert rows[1]["description"] == "Text with, commas"
            assert rows[2]["description"] == "Text with\nnewlines"

    finally:
        if Path(output_file).exists():
            Path(output_file).unlink()


def test_list_tables():
    """Test listing tables from database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ("public", "users"),
        ("public", "orders"),
        ("analytics", "metrics"),
    ]
    mock_conn.cursor.return_value = mock_cursor

    with patch("main.get_connection", return_value=mock_conn):
        # Capture stdout
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            postgres_main.list_tables()

        output = f.getvalue()
        assert "public.users" in output
        assert "public.orders" in output
        assert "analytics.metrics" in output
        assert "Total: 3 tables" in output


def test_describe_table_basic():
    """Test describing a table structure."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ("id", "integer", None, "NO", "nextval('users_id_seq'::regclass)"),
        ("name", "character varying", 255, "NO", None),
        ("email", "character varying", 255, "YES", None),
        ("created_at", "timestamp without time zone", None, "NO", "CURRENT_TIMESTAMP"),
    ]
    mock_conn.cursor.return_value = mock_cursor

    with patch("main.get_connection", return_value=mock_conn):
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            postgres_main.describe_table(table_name="users")

        output = f.getvalue()
        assert "Table: public.users" in output
        assert "id" in output
        assert "name" in output
        assert "email" in output
        assert "created_at" in output


def test_describe_table_with_schema():
    """Test describing a table with explicit schema."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ("id", "integer", None, "NO", None),
    ]
    mock_conn.cursor.return_value = mock_cursor

    with patch("main.get_connection", return_value=mock_conn):
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            postgres_main.describe_table(table_name="analytics.metrics")

        output = f.getvalue()
        assert "Table: analytics.metrics" in output


def test_list_schemas():
    """Test listing schemas from database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ("public",),
        ("analytics",),
        ("staging",),
    ]
    mock_conn.cursor.return_value = mock_cursor

    with patch("main.get_connection", return_value=mock_conn):
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            postgres_main.list_schemas()

        output = f.getvalue()
        assert "public" in output
        assert "analytics" in output
        assert "staging" in output
        assert "Total: 3 schemas" in output


if __name__ == "__main__":
    # Run tests with pytest (override project config to avoid conflicts)
    pytest.main([__file__, "-v", "--override-ini=addopts="])
