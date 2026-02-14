# test_database_connection  
# Use mock instead of real database

from unittest.mock import patch
from src.load_data import get_connection

def test_database_connection():
    with patch('src.load_data.psycopg.connect'):
        conn = get_connection()
        assert conn is not None
