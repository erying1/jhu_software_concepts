"""
Tests for query_data.py - Database query functions
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import query_data


@pytest.mark.db
def test_fmt_with_value():
    """Test fmt function with valid float"""
    assert query_data.fmt(3.14159) == "3.14"
    assert query_data.fmt(100.0) == "100.00"


@pytest.mark.db
def test_fmt_with_none():
    """Test fmt function with None returns N/A"""
    assert query_data.fmt(None) == "N/A"


@pytest.mark.db
@patch('src.query_data.psycopg.connect')
def test_get_connection(mock_connect):
    """Test database connection"""
    mock_conn = Mock()
    mock_connect.return_value = mock_conn
    
    conn = query_data.get_connection()
    
    assert conn == mock_conn


@pytest.mark.db
def test_q1_fall_2026_count():
    """Test Q1 query for Fall 2026 count"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (42,)
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    result = query_data.q1_fall_2026_count(mock_conn)
    
    assert result == 42
    assert mock_cursor.execute.called


@pytest.mark.db
def test_q2_percent_international():
    """Test Q2 query for international percentage"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (65.5,)
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    result = query_data.q2_percent_international(mock_conn)
    
    assert result == 65.5


@pytest.mark.db
def test_q2_percent_international_none():
    """Test Q2 handles None result"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (None,)
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    result = query_data.q2_percent_international(mock_conn)
    
    assert result == 0.0


@pytest.mark.db
def test_q3_average_metrics():
    """Test Q3 query for average metrics"""
    mock_conn = Mock()
    
    # Mock multiple cursor contexts for different queries
    mock_cursors = [Mock() for _ in range(4)]
    mock_cursors[0].fetchone.return_value = (3.75,)  # GPA
    mock_cursors[1].fetchone.return_value = (325.0,)  # GRE
    mock_cursors[2].fetchone.return_value = (162.5,)  # GRE V
    mock_cursors[3].fetchone.return_value = (4.5,)   # GRE AW
    
    cursor_iter = iter(mock_cursors)
    mock_conn.cursor.return_value.__enter__ = lambda self: next(cursor_iter)
    
    result = query_data.q3_average_metrics(mock_conn)
    
    assert result["avg_gpa"] == 3.75
    assert result["avg_gre"] == 325.0
    assert result["avg_gre_v"] == 162.5
    assert result["avg_gre_aw"] == 4.5
