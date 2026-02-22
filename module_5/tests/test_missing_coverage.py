"""Tests to achieve 100% coverage for queries.py and query_data.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.app.queries import get_all_results, compute_scraper_diagnostics
from src.query_data import ensure_table_exists, get_connection


def test_get_all_results_includes_timestamp(monkeypatch):
    """Test that get_all_results adds timestamp to results"""
    # Mock query_data.get_all_analysis to return fake data
    fake_results = {
        "q4": 3.5,
        "q5": 75.0,
    }

    monkeypatch.setattr("src.app.queries.qd.get_all_analysis", lambda: fake_results.copy())

    result = get_all_results()

    # Check that timestamp was added
    assert "timestamp" in result
    assert isinstance(result["timestamp"], str)
    # Check original data is still there
    assert result["q4"] == 3.5
    assert result["q5"] == 75.0


def test_compute_scraper_diagnostics_with_complete_records():
    """Test compute_scraper_diagnostics with records that have all fields"""
    records = [
        {
            "comments": "Great program",
            "term": "Fall 2026",
            "us_or_international": "American",
            "gpa": 3.8,
            "gre_total_score": 330,
            "gre_verbal_score": 165,
            "gre_aw_score": 5.0,
        },
        {
            "comments": "Good fit",
            "term": "Spring 2026",
            "us_or_international": "International",
            "gpa": 3.9,
            "gre_total_score": 335,
            "gre_verbal_score": 170,
            "gre_aw_score": 5.5,
        },
    ]

    result = compute_scraper_diagnostics(records)

    assert result["Total scraped rows"] == 2
    assert result["Comments present"] == 2
    assert result["Term present"] == 2
    assert result["Citizenship present"] == 2
    assert result["GPA present"] == 2
    assert result["GRE Total present"] == 2
    assert result["GRE Verbal present"] == 2
    assert result["GRE AW present"] == 2

    assert result["Comments missing"] == 0
    assert result["Term missing"] == 0
    assert result["Citizenship missing"] == 0
    assert result["GPA missing"] == 0
    assert result["GRE Total missing"] == 0
    assert result["GRE Verbal missing"] == 0
    assert result["GRE AW missing"] == 0


def test_compute_scraper_diagnostics_with_missing_fields():
    """Test compute_scraper_diagnostics with records missing some fields"""
    records = [
        {
            "comments": "Great",
            "term": None,
            "us_or_international": "",
            "gpa": 3.5,
            "gre_total_score": "null",
        },
        {
            "comments": None,
            "gpa": None,
        },
    ]

    result = compute_scraper_diagnostics(records)

    assert result["Total scraped rows"] == 2
    assert result["Comments present"] == 1
    assert result["Term present"] == 0
    assert result["Citizenship present"] == 0
    assert result["GPA present"] == 1
    assert result["GRE Total present"] == 0

    assert result["Comments missing"] == 1
    assert result["GPA missing"] == 1


@pytest.mark.db
def test_ensure_table_exists_creates_table():
    """Test that ensure_table_exists creates the applicants table"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    ensure_table_exists(mock_conn)

    # Verify cursor.execute was called with CREATE TABLE statement
    assert mock_cursor.execute.called
    call_args = mock_cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS applicants" in call_args
    assert "p_id SERIAL PRIMARY KEY" in call_args

    # Verify conn.commit was called
    assert mock_conn.commit.called


@pytest.mark.db
def test_ensure_table_exists_handles_exception():
    """Test that ensure_table_exists handles exceptions (e.g., permission denied)"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Make cursor.execute raise an exception (e.g., permission denied)
    mock_cursor.execute.side_effect = Exception("permission denied for schema public")

    # Should not raise - exception is caught and handled
    ensure_table_exists(mock_conn)

    # Verify conn.rollback was called
    assert mock_conn.rollback.called


@pytest.mark.db
@patch("src.query_data._real_get_connection")
@patch("src.query_data.ensure_table_exists")
def test_get_connection_calls_ensure_table(mock_ensure, mock_real_conn):
    """Test that get_connection calls ensure_table_exists"""
    mock_conn = Mock()
    mock_real_conn.return_value = mock_conn

    result = get_connection()

    # Verify _real_get_connection was called
    assert mock_real_conn.called

    # Verify ensure_table_exists was called with the connection
    mock_ensure.assert_called_once_with(mock_conn)

    # Verify the connection is returned
    assert result == mock_conn
