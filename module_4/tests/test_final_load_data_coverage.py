"""Final load_data.py coverage tests."""
import pytest
from unittest.mock import patch, Mock, MagicMock

def test_reset_database_with_active_connections():
    """Test reset_database terminates active connections."""
    from src.load_data import reset_database
    
    with patch('src.load_data.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        
        mock_connect.return_value = mock_conn
        
        reset_database("testdb")
        
        # Verify terminate, drop, and create were called
        assert mock_cursor.execute.call_count >= 3


def test_reset_database_full_flow():
    """Test complete reset_database flow."""
    from src.load_data import reset_database
    
    with patch('src.load_data.psycopg.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        mock_conn.close = MagicMock()
        
        mock_connect.return_value = mock_conn
        
        reset_database("studentCourses")
        
        # Verify connection to postgres
        call_kwargs = mock_connect.call_args[1]
        assert call_kwargs['dbname'] == 'postgres'
        assert call_kwargs['autocommit'] == True
        
        # Verify all SQL operations
        execute_calls = [str(call) for call in mock_cursor.execute.call_args_list]
        assert len(execute_calls) >= 3  # terminate, drop, create
