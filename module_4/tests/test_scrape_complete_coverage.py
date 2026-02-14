"""
Fixed comprehensive tests for scrape.py - matches actual function signatures.
Targets the missing lines in scrape.py.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import urllib.error


@pytest.mark.db
class TestScrapeDetailedCoverage:
    """Close coverage gaps in scrape.py"""
    
    # ==========================================================================
    # Lines 42-43: get_opener
    # ==========================================================================
    
    def test_get_opener_returns_opener(self):
        """Test get_opener returns a valid opener"""
        from src.module_2_1.scrape import get_opener
        
        result = get_opener()
        assert result is not None
    
    # ==========================================================================
    # Lines 47-53: check_robots paths
    # ==========================================================================
    
    @patch('urllib.robotparser.RobotFileParser')
    def test_check_robots_returns_true_when_allowed(self, mock_parser_class):
        """Test check_robots returns True when allowed"""
        from src.module_2_1.scrape import check_robots
        
        mock_parser = Mock()
        mock_parser.can_fetch.return_value = True
        mock_parser_class.return_value = mock_parser
        
        result = check_robots()
        assert result is True
    
    @patch('urllib.robotparser.RobotFileParser')
    def test_check_robots_with_exception_returns_true(self, mock_parser_class):
        """Test check_robots returns True on exception (fail-safe)"""
        from src.module_2_1.scrape import check_robots
        
        mock_parser = Mock()
        mock_parser.read.side_effect = Exception("Read error")
        mock_parser_class.return_value = mock_parser
        
        result = check_robots()
        assert result is True  # Should default to True on error
    
    # ==========================================================================
    # Lines 68-74, 78-84: get_html error handling
    # ==========================================================================
    
    def test_get_html_with_none_opener(self):
        """Test get_html with None opener uses internal _get_html"""
        from src.module_2_1.scrape import get_html
        
        with patch('src.module_2_1.scrape._get_html') as mock_internal:
            mock_internal.return_value = '<html>Test</html>'
            
            result = get_html('http://test.com', opener=None)
            
            mock_internal.assert_called_once()
    
    def test_get_html_with_opener_exception(self):
        """Test get_html handles opener exceptions"""
        from src.module_2_1.scrape import get_html
        
        mock_opener = Mock()
        mock_opener.open.side_effect = Exception("Network error")
        
        result = get_html('http://test.com', opener=mock_opener)
        assert result is None
    
    def test_get_html_with_opener_success(self):
        """Test get_html with valid opener"""
        from src.module_2_1.scrape import get_html
        
        mock_opener = Mock()
        mock_response = Mock()
        mock_response.read.return_value = b'<html>Test</html>'
        mock_opener.open.return_value = mock_response
        
        result = get_html('http://test.com', opener=mock_opener)
        assert result == '<html>Test</html>'
    
    # ==========================================================================
    # Lines 126-127, 134-135, 141: parse_row edge cases
    # ==========================================================================
    
    def test_parse_row_returns_none_without_link(self):
        """Test parse_row returns None when no link found"""
        from src.module_2_1.scrape import parse_row
        
        html = '<tr><td>No link here</td></tr>'
        soup = BeautifulSoup(html, 'html.parser')
        result = parse_row(soup.find('tr'), 'http://base.com')
        
        assert result is None
    
    def test_parse_row_returns_none_insufficient_columns(self):
        """Test parse_row returns None with < 4 columns"""
        from src.module_2_1.scrape import parse_row
        
        html = '''
        <tr>
            <td><a href="/result/123">Link</a></td>
            <td>Only two</td>
        </tr>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = parse_row(soup.find('tr'), 'http://base.com')
        
        assert result is None
    
    # ==========================================================================
    # Lines 155-156, 166-167, 173-178, 186-187, 190: parse_detail_page_html
    # ==========================================================================
    
    def test_parse_detail_page_html_with_base_url(self):
        """Test parse_detail_page_html adds entry_url when base_url provided"""
        from src.module_2_1.scrape import parse_detail_page_html
        
        with patch('src.module_2_1.scrape._get_html') as mock_get:
            mock_get.return_value = '<html><body><p>Test</p></body></html>'
            
            result = parse_detail_page_html('<html></html>', base_url='http://test.com')
            
            assert 'entry_url' in result
            assert result['entry_url'] == 'http://test.com'
    
    def test_parse_detail_page_html_without_base_url(self):
        """Test parse_detail_page_html without base_url"""
        from src.module_2_1.scrape import parse_detail_page_html
        
        with patch('src.module_2_1.scrape._get_html') as mock_get:
            mock_get.return_value = '<html><body><p>Test</p></body></html>'
            
            result = parse_detail_page_html('<html></html>')
            
            assert isinstance(result, dict)
    
    # ==========================================================================
    # Lines 213-214, 232-234, 246, 249-252: fetch_detail_batch
    # ==========================================================================
    
    @patch('src.module_2_1.scrape._parse_detail_page_html')
    def test_fetch_detail_batch_with_empty_records(self, mock_parse):
        """Test fetch_detail_batch with empty list"""
        from src.module_2_1.scrape import fetch_detail_batch
        
        result = fetch_detail_batch([])
        assert result == []
    
    @patch('src.module_2_1.scrape._parse_detail_page_html')
    def test_fetch_detail_batch_with_string_urls(self, mock_parse):
        """Test fetch_detail_batch converts string URLs to dict"""
        from src.module_2_1.scrape import fetch_detail_batch
        
        mock_parse.return_value = {'gpa': 3.5}
        
        result = fetch_detail_batch(['http://test1.com', 'http://test2.com'], max_workers=2)
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    @patch('src.module_2_1.scrape._parse_detail_page_html')
    def test_fetch_detail_batch_with_exceptions(self, mock_parse):
        """Test fetch_detail_batch handles exceptions gracefully"""
        from src.module_2_1.scrape import fetch_detail_batch
        
        # First call succeeds, second raises exception
        mock_parse.side_effect = [
            {'gpa': 3.5},
            Exception("Parse error")
        ]
        
        records = [
            {'entry_url': 'http://test1.com'},
            {'entry_url': 'http://test2.com'}
        ]
        
        result = fetch_detail_batch(records, max_workers=2)
        
        assert isinstance(result, list)
    
    # ==========================================================================
    # Lines 279, 282, 308-312, 344-347, 354, 394-400: scrape_data paths
    # ==========================================================================
    
    @patch('src.module_2_1.scrape._get_html')
    @patch('src.module_2_1.scrape.fetch_detail_batch')
    def test_scrape_data_basic_flow(self, mock_batch, mock_get):
        """Test scrape_data basic flow"""
        from src.module_2_1.scrape import scrape_data
        
        # Mock HTML with a table row
        mock_get.return_value = '''
        <html><body>
        <table>
            <tr>
                <td><a href="/result/123">Link</a></td>
                <td>University</td>
                <td>Program</td>
                <td>Date</td>
                <td>Accepted on 2024-01-01</td>
            </tr>
        </table>
        </body></html>
        '''
        
        mock_batch.return_value = [{'entry_url': 'http://test.com/result/123'}]
        
        result = scrape_data(max_entries=1, start_page=1, parallel_threads=2)
        
        assert isinstance(result, list)
    
    @patch('src.module_2_1.scrape._get_html')
    def test_scrape_data_no_html_returned(self, mock_get):
        """Test scrape_data when HTML fetch fails"""
        from src.module_2_1.scrape import scrape_data
        
        mock_get.return_value = None
        
        result = scrape_data(max_entries=10, start_page=1)
        
        assert isinstance(result, list)
    
    @patch('src.module_2_1.scrape._get_html')
    def test_scrape_data_exception_handling(self, mock_get):
        """Test scrape_data handles exceptions"""
        from src.module_2_1.scrape import scrape_data
        
        mock_get.side_effect = Exception("Network error")
        
        result = scrape_data(max_entries=10, start_page=1)
        
        assert isinstance(result, list)
    
    # ==========================================================================
    # Additional coverage for GRE total calculation
    # ==========================================================================
    
    def test_parse_detail_gre_total_calculation_with_valid_scores(self):
        """Test GRE total calculation"""
        from src.module_2_1.scrape import parse_detail_gre_total_calculation
        
        detail = {'gre_v': 165, 'gre_q': 170}
        result = parse_detail_gre_total_calculation(detail)
        
        assert result == 335
    
    def test_parse_detail_gre_total_calculation_with_none(self):
        """Test GRE total calculation with None"""
        from src.module_2_1.scrape import parse_detail_gre_total_calculation
        
        result = parse_detail_gre_total_calculation(None)
        assert result is None
    
    def test_parse_detail_gre_total_calculation_with_missing_scores(self):
        """Test GRE total calculation with missing scores"""
        from src.module_2_1.scrape import parse_detail_gre_total_calculation
        
        detail = {'gre_v': 165}  # Missing gre_q
        result = parse_detail_gre_total_calculation(detail)
        
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.module_2_1.scrape", "--cov-report=term-missing"])