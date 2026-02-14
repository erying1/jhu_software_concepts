# test_load_data_priority3.py

from unittest.mock import patch, Mock, MagicMock, call


def test_reset_database_executes_all_sql_commands():
    """Test reset_database runs all three SQL commands."""
    from src.load_data import reset_database
    
    with patch('src.load_data.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        
        mock_connect.return_value = mock_conn
        
        reset_database("testdb")
        
        # Verify exactly 3 SQL commands were executed
        assert mock_cursor.execute.call_count == 3
        
        # Verify the SQL commands in order
        calls = [str(call[0][0]).upper() for call in mock_cursor.execute.call_args_list]
        
        # Should have: terminate connections, drop database, create database
        assert any("PG_TERMINATE_BACKEND" in c or "TERMINATE" in c for c in calls), \
            "Should terminate connections"
        assert any("DROP DATABASE" in c for c in calls), \
            "Should drop database"
        assert any("CREATE DATABASE" in c for c in calls), \
            "Should create database"


def test_reset_database_closes_connection():
    """Test reset_database closes the connection."""
    from src.load_data import reset_database
    
    with patch('src.load_data.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        mock_conn.close = MagicMock()
        
        mock_connect.return_value = mock_conn
        
        reset_database("testdb")
        
        # Verify connection was closed
        mock_conn.close.assert_called_once()


def test_reset_database_uses_autocommit():
    """Test reset_database connects with autocommit=True."""
    from src.load_data import reset_database
    
    with patch('src.load_data.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        
        mock_connect.return_value = mock_conn
        
        reset_database("mydb")
        
        # Verify autocommit was set
        call_kwargs = mock_connect.call_args[1]
        assert call_kwargs.get('autocommit') is True
        assert call_kwargs.get('dbname') == 'postgres'