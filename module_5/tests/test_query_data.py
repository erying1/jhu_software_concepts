"""
Comprehensive tests for query_data.py functions.
These tests will significantly boost coverage from 49% to near 100%.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.query_data import q11_custom, q10_custom


@pytest.mark.db
def test_q4_avg_gpa_american_fall_2026():
    """Test q4: Average GPA of American students in Fall 2026."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (3.75,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q4_avg_gpa_american_fall_2026()
        assert result == "3.75"


@pytest.mark.db
def test_q4_avg_gpa_american_fall_2026_none():
    """Test q4 when no data available."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (None,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q4_avg_gpa_american_fall_2026()
        assert result == "N/A"


@pytest.mark.db
def test_q5_percent_accept_fall_2026():
    """Test q5: Percent of Fall 2026 entries that are Acceptances."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (25.5,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q5_percent_accept_fall_2026()
        assert result == "25.50"


@pytest.mark.db
def test_q5_percent_accept_fall_2026_none():
    """Test q5 when no data available."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (None,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q5_percent_accept_fall_2026()
        assert result == "N/A"


@pytest.mark.db
def test_q6_avg_gpa_accept_fall_2026():
    """Test q6: Average GPA of Fall 2026 Acceptances."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (3.85,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q6_avg_gpa_accept_fall_2026()
        assert result == "3.85"


@pytest.mark.db
def test_q6_avg_gpa_accept_fall_2026_none():
    """Test q6 when no data available."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (None,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q6_avg_gpa_accept_fall_2026()
        assert result == "N/A"


@pytest.mark.db
def test_q7_jhu_cs_masters_count():
    """Test q7: Count of JHU CS Masters entries."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (42,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q7_jhu_cs_masters_count()
        assert result == 42


@pytest.mark.db
def test_q7_jhu_cs_masters_count_none():
    """Test q7 when no data available."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (None,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q7_jhu_cs_masters_count()
        assert result == 0


@pytest.mark.db
def test_q8_elite_cs_phd_accepts_2026():
    """Test q8: Georgetown/MIT/Stanford/CMU CS PhD Acceptances 2026."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (5,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q8_elite_cs_phd_accepts_2026()
        assert result == 5


@pytest.mark.db
def test_q8_elite_cs_phd_accepts_2026_none():
    """Test q8 when no data available."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (None,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q8_elite_cs_phd_accepts_2026()
        assert result == 0


@pytest.mark.db
def test_q9_elite_cs_phd_llm_accepts_2026():
    """Test q9: Same as q8 but using LLM-generated fields."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (3,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q9_elite_cs_phd_llm_accepts_2026()
        assert result == 3


@pytest.mark.db
def test_q9_elite_cs_phd_llm_accepts_2026_none():
    """Test q9 when no data available."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (None,)
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.q9_elite_cs_phd_llm_accepts_2026()
        assert result == 0


def test_q10_custom(monkeypatch):
    """q10 should return grouped university counts"""
    # Fake DB rows returned by cursor.fetchall()
    fake_rows = [
        ("MIT", 5),
        ("Stanford", 3),
        ("JHU", 2),
    ]

    class FakeCursor:
        def execute(self, sql, params=None):
            # sql is a psycopg.sql.SQL object, convert to string for assertion
            sql_str = str(sql) if hasattr(sql, 'as_string') else str(sql)
            assert "llm_generated_university" in sql_str

        def fetchall(self):
            return fake_rows

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class FakeConn:
        def cursor(self):
            return FakeCursor()

    monkeypatch.setattr("src.query_data.get_connection", lambda: FakeConn())

    from src.query_data import q10_custom

    result = q10_custom()

    assert result == fake_rows
    assert len(result) == 3
    assert result[0] == ("MIT", 5)


def test_q11_custom(monkeypatch):
    """q11 should return degree acceptance summary"""

    fake_rows = [
        ("MS", 10, 7, 70.00),
        ("PhD", 5, 3, 60.00),
    ]

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, query, params=None):
            pass

        def fetchall(self):
            return fake_rows

    class FakeConn:
        def cursor(self):
            return FakeCursor()

    # Patch the connection before calling the function
    monkeypatch.setattr("src.query_data.get_connection", lambda: FakeConn())

    # Now execute the test
    result = q11_custom()

    # Assertions
    assert len(result) == 2
    assert result[0] == ("MS", 10, 7, 70.00)
    assert result[1] == ("PhD", 5, 3, 60.00)


@pytest.mark.db
def test_get_all_analysis():
    """Test get_all_analysis returns complete dict."""
    from src import query_data

    with patch("src.query_data.get_connection") as mock_conn:
        mock_cursor = Mock()
        # Mock responses for all queries
        mock_cursor.fetchone.side_effect = [
            (100,),  # q1
            (50.0,),  # q2
            (3.8, 320.0, 160.0, 4.5),  # q3
            (3.75,),  # q4
            (25.5,),  # q5
            (3.85,),  # q6
            (42,),  # q7
            (5,),  # q8
            (3,),  # q9
        ]
        mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        result = query_data.get_all_analysis()

        # Top-level keys
        assert "fall_2026_count" in result
        assert "pct_international" in result

        # Nested structure for avg_metrics
        assert "avg_metrics" in result
        assert "avg_gpa" in result["avg_metrics"]
        assert "avg_gre" in result["avg_metrics"]
        assert "avg_gre_v" in result["avg_metrics"]
        assert "avg_gre_aw" in result["avg_metrics"]

        # Other top-level keys
        assert "avg_gpa_american_fall_2026" in result
        assert "pct_accept_fall_2026" in result
        assert "avg_gpa_accept_fall_2026" in result
        assert "jhu_cs_masters_count" in result
        assert "elite_cs_phd_accepts_2026" in result
        assert "elite_cs_phd_llm_accepts_2026" in result
