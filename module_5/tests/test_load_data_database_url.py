"""
Test for load_data.py DATABASE_URL branch (line 72).
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.db
def test_get_connection_uses_database_url(monkeypatch):
    """Cover line 72: get_connection uses DATABASE_URL when set."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")

    mock_conn = MagicMock()
    with patch("src.load_data.psycopg.connect", return_value=mock_conn) as mock_connect:
        from src.load_data import get_connection

        conn = get_connection()
        mock_connect.assert_called_once_with(
            "postgresql://user:pass@localhost:5432/testdb"
        )
        assert conn is mock_conn
