"""
Tests for scrape.py - Web scraping functions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.module_2.1 import scrape
from bs4 import BeautifulSoup


@pytest.mark.integration
def test_get_opener():
    """Test opener creation"""
    opener = scrape.get_opener()
    assert opener is not None
    assert len(opener.addheaders) > 0


@pytest.mark.integration
@patch('src.module_2.1.scrape.urllib.robotparser.RobotFileParser')
def test_check_robots_allowed(mock_robot_parser):
    """Test robots.txt check when allowed"""
    mock_rp = Mock()
    mock_rp.can_fetch.return_value = True
    mock_robot_parser.return_value = mock_rp
    
    result = scrape.check_robots()
    
    assert result is True


@pytest.mark.integration
@patch('src.module_2.1.scrape.urllib.robotparser.RobotFileParser')
def test_check_robots_disallowed(mock_robot_parser):
    """Test robots.txt check when disallowed"""
    mock_rp = Mock()
    mock_rp.can_fetch.return_value = False
    mock_robot_parser.return_value = mock_rp
    
    result = scrape.check_robots()
    
    assert result is False


@pytest.mark.integration
@patch('src.module_2.1.scrape.get_opener')
@patch('time.sleep')
def test_get_html_success(mock_sleep, mock_get_opener):
    """Test HTML fetching succeeds"""
    mock_response = Mock()
    mock_response.read.return_value = b"<html>Test</html>"
    
    mock_opener = Mock()
    mock_opener.open.return_value.__enter__.return_value = mock_response
    mock_get_opener.return_value = mock_opener
    
    html = scrape._get_html("http://test.com")
    
    assert html == "<html>Test</html>"


@pytest.mark.integration
@patch('src.module_2.1.scrape.get_opener')
@patch('time.sleep')
def test_get_html_failure(mock_sleep, mock_get_opener):
    """Test HTML fetching handles errors"""
    mock_opener = Mock()
    mock_opener.open.side_effect = Exception("Network error")
    mock_get_opener.return_value = mock_opener
    
    html = scrape._get_html("http://test.com")
    
    assert html == ""


@pytest.mark.integration
def test_parse_row_valid():
    """Test parsing a valid table row"""
    html = """
    <tr>
        <td>
            <a href="/result/12345">Link</a>
            <div class="tw-font-medium">Stanford University</div>
        </td>
        <td>
            <div>
                <span>Computer Science</span>
                <span>PhD</span>
            </div>
        </td>
        <td>15 Jan 2026</td>
        <td>Accepted on 15 Jan</td>
    </tr>
    """
    
    soup = BeautifulSoup(html, "html.parser")
    tr = soup.find("tr")
    
    result = scrape._parse_row(tr, "https://www.thegradcafe.com/survey/")
    
    assert result is not None
    assert result["university"] == "Stanford University"
    assert result["program_name"] == "Computer Science"
    assert result["degree_level"] == "PhD"
    assert result["status"] == "Accepted"
    assert result["date_added"] == "15 Jan 2026"


@pytest.mark.integration
def test_parse_row_no_link():
    """Test parsing row without link returns None"""
    html = "<tr><td>No link here</td></tr>"
    soup = BeautifulSoup(html, "html.parser")
    tr = soup.find("tr")
    
    result = scrape._parse_row(tr, "https://test.com")
    
    assert result is None


@pytest.mark.integration
def test_parse_row_insufficient_columns():
    """Test parsing row with too few columns"""
    html = """
    <tr>
        <td><a href="/result/1">Link</a></td>
        <td>Only</td>
    </tr>
    """
    soup = BeautifulSoup(html, "html.parser")
    tr = soup.find("tr")
    
    result = scrape._parse_row(tr, "https://test.com")
    
    assert result is None


@pytest.mark.integration
@patch('src.module_2.1.scrape._get_html')
def test_parse_detail_page_html(mock_get_html):
    """Test parsing detail page HTML"""
    mock_get_html.return_value = """
    <html>
        <div>GPA: 3.85</div>
        <div>International student</div>
        <div>GRE V: 165</div>
        <div>Fall 2026</div>
    </html>
    """
    
    result = scrape._parse_detail_page_html("http://test.com/result/1")
    
    assert result["gpa"] == 3.85
    assert result["citizenship"] == "International"
    assert result["gre_v"] == 165
    assert "Fall 2026" in result["term"]


@pytest.mark.integration
@patch('src.module_2.1.scrape._get_html')
def test_parse_detail_page_empty_html(mock_get_html):
    """Test parsing detail page with empty HTML"""
    mock_get_html.return_value = ""
    
    result = scrape._parse_detail_page_html("http://test.com/result/1")
    
    # Should return defaults
    assert result["gpa"] is None
    assert result["citizenship"] is None


@pytest.mark.integration
def test_parse_detail_page_html_no_url():
    """Test parsing with no URL"""
    result = scrape._parse_detail_page_html("")
    
    assert result["gpa"] is None


@pytest.mark.integration
@patch('src.module_2.1.scrape._parse_detail_page_html')
def test_fetch_detail_batch(mock_parse):
    """Test parallel detail fetching"""
    records = [
        {"entry_url": "http://test.com/1"},
        {"entry_url": "http://test.com/2"}
    ]
    
    mock_parse.return_value = {
        "gpa": 3.9,
        "citizenship": "International",
        "term": None,
        "comments": None,
        "gre_total": None,
        "gre_v": 165,
        "gre_q": None,
        "gre_aw": None
    }
    
    result = scrape.fetch_detail_batch(records, max_workers=2)
    
    assert len(result) == 2
    assert result[0]["gpa"] == 3.9


@pytest.mark.integration
@patch('src.module_2.1.scrape.check_robots')
@patch('src.module_2.1.scrape._get_html')
@patch('builtins.open', create=True)
def test_scrape_data_basic(mock_open, mock_get_html, mock_robots):
    """Test basic scraping function"""
    mock_robots.return_value = True
    
    # Mock listing page HTML
    mock_get_html.return_value = """
    <table>
        <tr>
            <td>
                <a href="/result/1">Link</a>
                <div class="tw-font-medium">MIT</div>
            </td>
            <td>
                <div><span>CS</span><span>PhD</span></div>
            </td>
            <td>15 Jan</td>
            <td>Accepted on 15 Jan</td>
        </tr>
    </table>
    """
    
    result = scrape.scrape_data(max_entries=1, parallel_threads=1)
    
    assert len(result) <= 1
    if len(result) > 0:
        assert "university" in result[0]


@pytest.mark.integration
def test_parse_detail_gre_total_calculation():
    """Test GRE total is calculated from V and Q"""
    html = """
    <div>GRE V: 165</div>
    <div>GRE Q: 168</div>
    """
    
    with patch('src.module_2.1.scrape._get_html', return_value=html):
        result = scrape._parse_detail_page_html("http://test.com")
        
        assert result["gre_v"] == 165
        assert result["gre_q"] == 168
        assert result["gre_total"] == 333
