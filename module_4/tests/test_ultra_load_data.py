"""Ultra-targeted load_data.py tests."""
import pytest
from unittest.mock import patch, Mock, MagicMock


def test_reset_database_drop_command():
    """Test reset_database executes DROP DATABASE."""
    from src.load_data import reset_database
    
    with patch('src.load_data.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        
        mock_connect.return_value = mock_conn
        
        reset_database("testdb")
        
        execute_calls = [str(call) for call in mock_cursor.execute.call_args_list]
        assert any("DROP DATABASE" in call.upper() for call in execute_calls)


def test_reset_database_create_command():
    """Test reset_database executes CREATE DATABASE."""
    from src.load_data import reset_database
    
    with patch('src.load_data.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        
        mock_connect.return_value = mock_conn
        
        reset_database("newdb")
        
        execute_calls = [str(call) for call in mock_cursor.execute.call_args_list]
        assert any("CREATE DATABASE" in call.upper() for call in execute_calls)
