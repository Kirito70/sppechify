"""
Database connection tests
"""
import pytest
import psycopg2


def test_database_connection(db_connection):
    """Test that database connection works."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    assert "PostgreSQL" in version
    cursor.close()


def test_database_name(db_connection):
    """Test that we're connected to the correct database."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()[0]
    assert db_name == "japanese_learning"
    cursor.close()


def test_database_tables_exist(db_connection):
    """Test that we can query the table structure."""
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    # For now, just check that we can query without error
    # As we add models, we can test for specific tables
    assert isinstance(tables, list)
    cursor.close()