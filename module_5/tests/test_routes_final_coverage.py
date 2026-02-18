"""
Tests for routes.py remaining uncovered lines: 65, 121, 200.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.mark.analysis
def test_pct_none_returns_na():
    """Cover line 65: pct(None) returns 'N/A'."""
    from src.app.routes import pct

    assert pct(None) == "N/A"


@pytest.mark.web
def test_pull_data_busy_json_response(client, monkeypatch):
    """Cover line 121: JSON 409 when pull_data is called while busy."""
    from src.app import routes

    monkeypatch.setattr(routes, "pull_running", True)

    response = client.post(
        "/pull-data",
        content_type="application/json",
        data="{}",
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["busy"] is True


@pytest.mark.web
def test_update_analysis_busy_html_redirect(client, monkeypatch):
    """Cover line 200: non-JSON redirect when update_analysis is called while busy."""
    from src.app import routes

    monkeypatch.setattr(routes, "pull_running", True)

    response = client.post(
        "/update-analysis",
        headers={"Accept": "text/html"},
    )
    assert response.status_code == 302
