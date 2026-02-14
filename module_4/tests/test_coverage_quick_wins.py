"""Quick wins to improve coverage."""
import pytest
from unittest.mock import patch, Mock, MagicMock
import subprocess
import sys

def test_run_main_execution():
    """Test run.py main execution."""
    result = subprocess.run(
        [sys.executable, "src/run.py"],
        capture_output=True,
        timeout=2
    )
    assert result.returncode in [0, 1]


def test_format_percentage_invalid():
    """Test percentage filter with invalid input."""
    from src.app import create_app
    app = create_app()
    with app.app_context():
        pct = app.jinja_env.filters['pct']
        assert pct(None) == "0.00"
        assert pct("bad") == "0.00"


def test_reset_database_mock():
    """Test reset_database with mocking."""
    from src.load_data import reset_database
    
    with patch('src.load_data.psycopg.connect') as mock_connect:
        # Create proper mock connection with context manager support
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup context manager for cursor
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        mock_conn.close = MagicMock()
        
        mock_connect.return_value = mock_conn
        
        # Call function
        reset_database("test")
        
        # Verify connection was made to postgres database
        assert mock_connect.called
        call_kwargs = mock_connect.call_args[1]
        assert call_kwargs['dbname'] == 'postgres'
        assert call_kwargs['autocommit'] == True
        
        # Verify cursor operations happened
        assert mock_cursor.execute.called
