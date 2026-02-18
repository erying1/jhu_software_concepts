"""
Test for pages.py render_analysis_page function.
"""

import pytest


@pytest.mark.analysis
def test_render_analysis_page():
    """Cover all branches in render_analysis_page."""
    from src.app.pages import render_analysis_page

    html = render_analysis_page({"Q1": "42", "Q2": "3.14"}, busy=False)
    assert "Pull Data" in html
    assert "Update Analysis" in html
    assert "Answer:" in html
    assert "42" in html

    # Test busy state disables buttons
    html_busy = render_analysis_page({}, busy=True)
    assert "disabled" in html_busy
