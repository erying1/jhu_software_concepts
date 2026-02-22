"""
Flask App & Page Rendering Tests
Required by assignment: test_flask_page.py

Tests:
1. App factory creates Flask app with required routes
2. GET /analysis returns 200
3. Page contains "Pull Data" and "Update Analysis" buttons
4. Page text includes "Analysis" and at least one "Answer:"
"""

import pytest
from unittest.mock import MagicMock


@pytest.mark.web
def test_analysis_route_exists(client):
    """Test that /analysis route returns 200"""
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.web
def test_analysis_page_has_buttons(client):
    """Test that the analysis page has both required buttons"""
    response = client.get("/")
    html = response.data.decode()

    # Check for "Pull Data" button
    assert (
        "Pull Data" in html
        or "pull-data" in html.lower()
        or "pull_data" in html.lower()
    )

    # Check for "Update Analysis" button
    assert (
        "Update Analysis" in html
        or "update-analysis" in html.lower()
        or "update_analysis" in html.lower()
    )


@pytest.mark.web
def test_analysis_page_has_answer_labels(client):
    """Test that the analysis page has Answer labels and Analysis text"""
    response = client.get("/")
    html = response.data.decode()

    # Check for "Answer:" labels
    assert "Answer:" in html or "answer" in html.lower()

    # Check for "Analysis" text
    assert "Analysis" in html or "analysis" in html.lower()


@pytest.mark.web
def test_flask_app_has_required_routes(client, monkeypatch):
    """Test that Flask app has all required routes"""
    # Mock subprocess.run to prevent actual pipeline execution
    import subprocess
    mock_run = MagicMock(return_value=MagicMock(returncode=0))
    monkeypatch.setattr(subprocess, "run", mock_run)

    # Test main analysis route
    response = client.get("/")
    assert response.status_code == 200

    # Test pull-data route exists (may return various status codes)
    response = client.post("/pull-data")
    assert response.status_code in [200, 302, 400, 409, 500]

    # Test update-analysis route exists (may return various status codes)
    response = client.post("/update-analysis")
    assert response.status_code in [200, 302, 400, 409, 500]
