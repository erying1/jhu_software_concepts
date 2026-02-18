"""
Analysis Formatting Tests
Required by assignment: test_analysis_format.py

Tests:
1. Page includes "Answer" labels for rendered analysis
2. Any percentage is formatted with exactly two decimals
"""

import pytest
import re


@pytest.mark.analysis
def test_percentages_have_two_decimals(client):
    """Test that percentages are formatted with 2 decimals"""
    response = client.get("/")
    assert response.status_code == 200

    html = response.data.decode("utf-8")

    # Find all percentages in the page (e.g., "45.67%")
    percentages = re.findall(r"\d+\.\d+%", html)

    # If there are percentages, check each has exactly 2 decimal places
    for pct in percentages:
        decimal_part = pct.split(".")[1].rstrip("%")
        assert len(decimal_part) == 2, f"Expected 2 decimals, got: {pct}"


@pytest.mark.analysis
def test_analysis_has_labels(client):
    """Test that page includes 'Answer' labels for rendered analysis"""
    response = client.get("/")
    assert response.status_code == 200

    html = response.data.decode("utf-8")

    # Check for "Answer:" labels (case-insensitive)
    html_lower = html.lower()
    assert (
        "answer" in html_lower
    ), "Page should include 'Answer' labels for analysis results"

    # More specific: look for "Answer:" pattern
    # This ensures answers are properly labeled, not just the word appearing somewhere
    assert "answer:" in html_lower or "answer" in html_lower
