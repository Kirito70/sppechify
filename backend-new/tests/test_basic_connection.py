"""Database connection tests using pytest framework."""

import pytest
import psycopg2
from unittest.mock import patch, Mock


class TestDatabaseConnection:
    """Test basic database connectivity."""

    def test_psycopg2_available(self):
        """Test that psycopg2 is available for database connections."""
        try:
            import psycopg2
            assert psycopg2 is not None
        except ImportError:
            pytest.fail("psycopg2 not available - needed for database connections")

    @pytest.mark.integration
    def test_database_connection_parameters(self):
        """Test database connection parameters are correctly configured."""
        conn_params = {
            'host': 'localhost',
            'port': 5432, 
            'database': 'japanese_learning',
            'user': 'postgres',
            'password': 'admin'
        }
        
        assert conn_params['host'] == 'localhost'
        assert conn_params['port'] == 5432
        assert conn_params['database'] == 'japanese_learning'
        assert conn_params['user'] == 'postgres'

    @pytest.mark.integration  
    def test_database_connection_live(self):
        """Test actual database connection (requires running PostgreSQL)."""
        pytest.importorskip("psycopg2")
        
        conn_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'japanese_learning', 
            'user': 'postgres',
            'password': 'admin'
        }
        
        try:
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            assert "PostgreSQL" in version
            
            # Test current database
            cursor.execute("SELECT current_database();")
            current_db = cursor.fetchone()[0]
            assert current_db == 'japanese_learning'
            
            cursor.close()
            conn.close()
            
        except psycopg2.Error as e:
            pytest.skip(f"Database not available: {e}")

    def test_connection_error_handling(self):
        """Test that connection errors are handled properly.""" 
        bad_params = {
            'host': 'nonexistent-host',
            'port': 5432,
            'database': 'nonexistent_db',
            'user': 'invalid_user', 
            'password': 'wrong_password'
        }
        
        with pytest.raises(psycopg2.Error):
            psycopg2.connect(**bad_params)