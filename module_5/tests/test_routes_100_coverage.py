"""
Additional tests to achieve 100% coverage for routes.py
Covers the remaining 7 uncovered lines.
"""

import pytest
from unittest.mock import MagicMock, mock_open, patch


@pytest.mark.web
def test_get_last_analysis_file_not_exists(monkeypatch):
    """Line 80: get_last_analysis returns None when file doesn't exist"""
    from src.app import routes

    # Mock os.path.exists to return False
    monkeypatch.setattr("os.path.exists", lambda path: False)

    result = routes.get_last_analysis()
    assert result is None


@pytest.mark.web
def test_pull_data_file_not_found_non_json(client, monkeypatch):
    """Lines 277-280: FileNotFoundError handler for non-JSON request in pull_data"""
    from src.app import routes
    import subprocess

    # Mock subprocess.run to raise FileNotFoundError
    def mock_run(*args, **kwargs):
        raise FileNotFoundError("scrape.py not found")

    monkeypatch.setattr(subprocess, "run", mock_run)

    # Non-JSON request (regular form submission)
    response = client.post("/pull-data")

    # Should redirect with flash message (302) or return 500
    assert response.status_code in [302, 500]


@pytest.mark.web
def test_pull_data_file_not_found_json_request(client, monkeypatch):
    """Line 279: FileNotFoundError handler for JSON request in pull_data"""
    from src.app import routes
    import subprocess

    # Mock subprocess.run to raise FileNotFoundError
    def mock_run(*args, **kwargs):
        raise FileNotFoundError("scrape.py not found")

    monkeypatch.setattr(subprocess, "run", mock_run)

    # JSON request (AJAX call)
    response = client.post(
        "/pull-data",
        headers={"Content-Type": "application/json"},
        json={}
    )

    # Should return JSON error with 500 status
    assert response.status_code == 500
    data = response.get_json()
    assert data["ok"] is False
    assert "File not found" in data["error"]


@pytest.mark.web
def test_update_analysis_timestamp_write_fails(client, monkeypatch):
    """Lines 333-334: OSError when writing analysis timestamp"""
    from src.app import routes

    # Mock get_all_results to return valid data
    monkeypatch.setattr(
        routes,
        "get_all_results",
        lambda: {"avg_metrics": {}}
    )
    monkeypatch.setattr(routes, "load_scraped_records", lambda: [])
    monkeypatch.setattr(routes, "compute_scraper_diagnostics", lambda x: {})

    # Mock open to raise OSError when writing timestamp
    original_open = open
    def mock_open_func(file, mode='r', *args, **kwargs):
        if 'last_analysis.txt' in str(file) and 'w' in mode:
            raise OSError("Permission denied")
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open_func)

    # Should succeed despite OSError (error is caught and passed)
    response = client.post("/update-analysis")
    assert response.status_code in [200, 302]
