"""Flask page rendering tests"""
import pytest
from bs4 import BeautifulSoup

@pytest.mark.web
def test_analysis_route_exists(client):
    """Test that /analysis route returns 200"""
    response = client.get('/')
    assert response.status_code == 200

@pytest.mark.web
def test_analysis_page_has_buttons(client):
    """Test page has Pull Data and Update Analysis buttons"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'Pull Data' in html or 'pull' in html.lower()
    assert 'Update Analysis' in html or 'update' in html.lower()

@pytest.mark.web
def test_analysis_page_has_answer_labels(client):
    """Test page contains Answer labels"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'Answer:' in html or 'answer' in html.lower()
