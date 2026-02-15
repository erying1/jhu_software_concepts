"""
Tests to cover load_data.py main() function and error paths.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import load_data


@pytest.mark.analysis
def test_load_data_main_success(monkeypatch):
    """Cover main() happy path — load_into_db succeeds."""
    monkeypatch.setattr(load_data, "load_into_db", lambda filepath: None)

    result = load_data.main()
    assert result == "load_data_main_executed"


@pytest.mark.analysis
def test_load_data_main_error(monkeypatch):
    """Cover main() except branch — load_into_db raises."""
    def failing_load(filepath):
        raise RuntimeError("DB connection failed")

    monkeypatch.setattr(load_data, "load_into_db", failing_load)

    result = load_data.main()
    assert "error" in result
    assert "DB connection failed" in result


@pytest.mark.analysis
def test_load_data_main_with_drop(monkeypatch):
    """Cover main(drop=True) — reset_database is called first."""
    calls = []

    monkeypatch.setattr(load_data, "reset_database", lambda dbname: calls.append("reset"))
    monkeypatch.setattr(load_data, "load_into_db", lambda filepath: calls.append("load"))

    result = load_data.main(drop=True)
    assert result == "load_data_main_executed"
    assert calls == ["reset", "load"]
