"""
Tests for load_data.py - Database loading functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import load_data
from tests.test_helpers import create_mock_connection


@pytest.mark.db
def test_load_json_success(tmp_path):
    """Test loading valid JSON file"""
    test_file = tmp_path / "test.json"
    test_data = [{"program": "CS", "university": "MIT"}]
    test_file.write_text(json.dumps(test_data))

    result = load_data.load_json(str(test_file))
    assert result == test_data


@pytest.mark.db
def test_load_json_file_not_found():
    """Test loading non-existent file raises FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        load_data.load_json("/nonexistent/file.json")


@pytest.mark.db
def test_normalize_record():
    """Test record normalization maps fields correctly"""
    raw = {
        "program_name": "Computer Science",
        "university": "MIT",
        "comments": "Great program",
        "date_added": "2026-01-15",
        "entry_url": "http://test.com/1",
        "status": "Accepted",
        "status_date": "15 Jan",
        "term": "Fall 2026",
        "citizenship": "International",
        "gpa": 3.9,
        "gre_total": 330,
        "gre_v": 165,
        "gre_aw": 5.0,
        "degree_level": "PhD",
        "llm-generated-program": "Computer Science",
        "llm-generated-university": "Massachusetts Institute of Technology",
    }

    result = load_data.normalize_record(raw)

    assert result["program"] == "Computer Science"
    assert result["url"] == "http://test.com/1"
    assert result["us_or_international"] == "International"
    assert result["degree"] == "PhD"
    assert result["llm_generated_program"] == "Computer Science"


@pytest.mark.db
def test_normalize_record_with_alternative_keys():
    """Test normalization handles alternative key names"""
    raw = {
        "program": "Physics",  # Not program_name
        "llm_generated_program": "Physics",  # Underscore version
        "llm_generated_university": "Harvard",
    }

    result = load_data.normalize_record(raw)
    assert result["program"] == "Physics"
    assert result["llm_generated_program"] == "Physics"


@pytest.mark.db
@patch.dict(
    "os.environ",
    {
        "DATABASE_URL": "",
        "DB_NAME": "studentCourses",
        "DB_USER": "postgres",
        "DB_PASSWORD": "testpassword",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
    },
)
@patch("src.load_data.psycopg.connect")
def test_get_connection(mock_connect):
    """Test database connection creation"""
    mock_conn = Mock()
    mock_connect.return_value = mock_conn

    conn = load_data.get_connection()

    assert conn == mock_conn
    mock_connect.assert_called_once_with(
        dbname="studentCourses",
        user="postgres",
        password="testpassword",
        host="localhost",
        port=5432,
    )


@pytest.mark.db
@patch("src.load_data.psycopg.connect")
def test_create_table(mock_connect):
    """Test table creation SQL"""
    mock_conn = create_mock_connection()
    mock_connect.return_value = mock_conn

    load_data.create_table(mock_conn)

    # Verify commit was called
    mock_conn.commit.assert_called_once()


@pytest.mark.db
@patch("src.load_data.psycopg.connect")
def test_insert_record_new(mock_connect):
    """Test inserting a new record returns 1"""
    from tests.test_helpers import create_mock_cursor

    mock_conn = MagicMock()
    mock_cursor = create_mock_cursor(rowcount=1)
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None

    record = {"program": "CS", "url": "http://test.com/1", "gpa": 3.9}

    result = load_data.insert_record(mock_conn, record)

    assert result == 1
    assert mock_cursor.execute.called
    mock_conn.commit.assert_called_once()


@pytest.mark.db
@patch("src.load_data.psycopg.connect")
def test_insert_record_duplicate(mock_connect):
    """Test inserting duplicate record returns 0"""
    from tests.test_helpers import create_mock_cursor

    mock_conn = MagicMock()
    mock_cursor = create_mock_cursor(rowcount=0)
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None

    record = {"program": "CS", "url": "http://test.com/1"}

    result = load_data.insert_record(mock_conn, record)

    assert result == 0


@pytest.mark.db
@patch("src.load_data.get_connection")
@patch("src.load_data.load_json")
def test_load_into_db(mock_load_json, mock_get_conn):
    """Test full load pipeline"""
    # Mock data
    mock_data = [
        {"program_name": "CS", "entry_url": "http://test.com/1"},
        {"program_name": "Physics", "entry_url": "http://test.com/2"},
    ]
    mock_load_json.return_value = mock_data

    # Mock connection with proper context manager
    mock_conn = create_mock_connection()
    mock_get_conn.return_value = mock_conn

    # Run
    load_data.load_into_db("test.json")

    # Verify
    mock_load_json.assert_called_once_with("test.json")
    mock_conn.close.assert_called_once()


@pytest.mark.db
@patch("src.load_data.psycopg.connect")
def test_reset_database(mock_connect):
    """Test database reset functionality"""
    mock_conn = create_mock_connection()
    mock_connect.return_value = mock_conn

    load_data.reset_database("studentCourses")

    # Should have closed connection
    mock_conn.close.assert_called_once()


@pytest.mark.db
def test_normalize_record_handles_none_values():
    """Test that normalization handles missing fields gracefully"""
    raw = {}
    result = load_data.normalize_record(raw)

    # Should return dict with None values
    assert result["program"] is None
    assert result["url"] is None
    assert result["gpa"] is None
