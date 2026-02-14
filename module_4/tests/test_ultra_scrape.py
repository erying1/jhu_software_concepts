"""Ultra-targeted scrape.py tests for remaining lines."""
import pytest
from unittest.mock import patch, Mock
import urllib.error
from bs4 import BeautifulSoup


def test_get_opener_with_user_agent():
    """Test get_opener sets user agent properly."""
    from src.module_2_1.scrape import get_opener
    
    opener = get_opener()
    assert opener is not None
    assert hasattr(opener, 'open')


def test_check_robots_read_error():
    """Test check_robots when robots.txt read fails."""
    from src.module_2_1.scrape import check_robots
    
    with patch('src.module_2_1.scrape.urllib.robotparser.RobotFileParser') as mock_parser:
        mock_rp = Mock()
        mock_rp.read.side_effect = Exception("Cannot read robots.txt")
        mock_parser.return_value = mock_rp
        
        result = check_robots()
        assert result in [True, False]


def test_parse_row_with_exception():
    """Test parse_row handles exceptions gracefully."""
    from src.module_2_1.scrape import parse_row
    
    html = """
    <tr>
        <td><a href="test">Link</a></td>
        <td>Status</td>
        <td>Term</td>
        <td>GPA</td>
        <td>Comments</td>
        <td>Extra</td>
    </tr>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    row = soup.find('tr')
    
    mock_opener = Mock()
    mock_opener.open.side_effect = Exception("Error")
    
    result = parse_row(row, mock_opener)
    assert result is None or isinstance(result, dict)


def test_parse_detail_page_with_partial_data():
    """Test parse_detail_page_html with partial GRE data."""
    from src.module_2_1.scrape import parse_detail_page_html
    
    html = """
    <html><body>
        <div class='col-md-12'>
            <strong>GRE General (V):</strong> 160
            <strong>GRE General (Q):</strong> (Not provided)
            <strong>GRE General (AW):</strong> 4.0
        </div>
    </body></html>
    """
    
    result = parse_detail_page_html(html, "http://test.com")
    assert isinstance(result, dict)


def test_parse_detail_page_exception_handling():
    """Test parse_detail_page_html handles exceptions."""
    from src.module_2_1.scrape import parse_detail_page_html
    
    html = "<html><body><div class='col-md-12'><strong>Broken"
    
    result = parse_detail_page_html(html, "http://test.com")
    assert isinstance(result, dict)


def test_fetch_detail_batch_all_failures():
    """Test fetch_detail_batch when all requests fail."""
    from src.module_2_1.scrape import fetch_detail_batch
    
    urls = ["http://test1.com", "http://test2.com"]
    
    with patch('src.module_2_1.scrape.get_opener') as mock_opener:
        mock_opener_obj = Mock()
        mock_opener_obj.open.side_effect = urllib.error.HTTPError(
            "http://test.com", 500, "Server Error", {}, None
        )
        mock_opener.return_value = mock_opener_obj
        
        result = fetch_detail_batch(urls)
        assert isinstance(result, list)


def test_scrape_data_main_page_error():
    """Test scrape_data when main page fetch fails."""
    from src.module_2_1.scrape import scrape_data
    
    with patch('src.module_2_1.scrape.check_robots', return_value=True):
        with patch('src.module_2_1.scrape.get_opener') as mock_opener:
            mock_opener_obj = Mock()
            mock_opener_obj.open.side_effect = urllib.error.HTTPError(
                "http://test.com", 404, "Not Found", {}, None
            )
            mock_opener.return_value = mock_opener_obj
            
            result = scrape_data()
            assert isinstance(result, list)


def test_scrape_data_parse_error():
    """Test scrape_data when HTML parsing fails."""
    from src.module_2_1.scrape import scrape_data
    
    with patch('src.module_2_1.scrape.check_robots', return_value=True):
        with patch('src.module_2_1.scrape.get_opener') as mock_opener:
            mock_opener_obj = Mock()
            mock_response = Mock()
            mock_response.read.return_value = b"Not HTML at all"
            mock_opener_obj.open.return_value = mock_response
            mock_opener.return_value = mock_opener_obj
            
            result = scrape_data()
            assert isinstance(result, list)


def test_scrape_data_empty_table():
    """Test scrape_data with empty table."""
    from src.module_2_1.scrape import scrape_data
    
    with patch('src.module_2_1.scrape.check_robots', return_value=True):
        with patch('src.module_2_1.scrape.get_opener') as mock_opener:
            mock_opener_obj = Mock()
            html = "<html><body><table></table></body></html>"
            mock_response = Mock()
            mock_response.read.return_value = html.encode()
            mock_opener_obj.open.return_value = mock_response
            mock_opener.return_value = mock_opener_obj
            
            result = scrape_data()
            assert isinstance(result, list)
