"""
Comprehensive tests for scrape.py uncovered lines
"""
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup


# =============================================================================
# Line 53: Return str(data) path in get_html
# =============================================================================

@pytest.mark.db
def test_get_html_with_string_data():
    """Line 53: get_html returns str(data) when data is not bytes"""
    from src.module_2_1.scrape import get_html
    
    # Mock opener that returns non-bytes data
    mock_opener = Mock()
    mock_response = Mock()
    mock_response.read.return_value = "already a string"  # Not bytes
    mock_opener.open.return_value = mock_response
    
    result = get_html("http://test.com", opener=mock_opener)
    assert result == "already a string"


# =============================================================================
# Lines 130-131: Exception in GPA parsing
# =============================================================================

@pytest.mark.db
def test_parse_detail_gpa_exception_handling():
    """Lines 130-131: Exception handler in GPA parsing"""
    from src.module_2_1.scrape import parse_detail_page_html
    
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # HTML that triggers exception during float conversion
        mock_get.return_value = '''
        <html><body>
            <div>GPA: invalid_number</div>
        </body></html>
        '''
        
        result = parse_detail_page_html('http://test.com', base_url='http://test.com')
        # Should not crash, GPA should be None
        assert result['gpa'] is None


# =============================================================================
# Lines 138-139: American citizenship detection
# =============================================================================

@pytest.mark.db
def test_parse_detail_american_citizenship():
    """Lines 138-139: Detect American/Domestic citizenship"""
    from src.module_2_1.scrape import parse_detail_page_html
    
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # Test "american"
        mock_get.return_value = '<html><body><div>Citizenship: American</div></body></html>'
        result = parse_detail_page_html('http://test.com', base_url='http://test.com')
        assert result['citizenship'] == "American"
        
        # Test "domestic"
        mock_get.return_value = '<html><body><div>Status: Domestic Student</div></body></html>'
        result = parse_detail_page_html('http://test.com', base_url='http://test.com')
        assert result['citizenship'] == "American"
        
        # Test "u.s"
        mock_get.return_value = '<html><body><div>Citizenship: U.S. Citizen</div></body></html>'
        result = parse_detail_page_html('http://test.com', base_url='http://test.com')
        assert result['citizenship'] == "American"


# =============================================================================
# Lines 159-160: Exception in GRE Verbal parsing
# =============================================================================

@pytest.mark.db
def test_parse_detail_gre_verbal_exception():
    """Lines 159-160: Exception handler in GRE Verbal parsing"""
    from src.module_2_1.scrape import parse_detail_page_html
    
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # HTML with invalid GRE V value
        mock_get.return_value = '<html><body><div>GRE V: abc</div></body></html>'
        
        result = parse_detail_page_html('http://test.com', base_url='http://test.com')
        assert result['gre_v'] is None


# =============================================================================
# Lines 170-171: Exception in GRE Quant parsing
# =============================================================================

@pytest.mark.db
def test_parse_detail_gre_quant_exception():
    """Lines 170-171: Exception handler in GRE Quant parsing"""
    from src.module_2_1.scrape import parse_detail_page_html
    
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # HTML with invalid GRE Q value
        mock_get.return_value = '<html><body><div>GRE Q: xyz</div></body></html>'
        
        result = parse_detail_page_html('http://test.com', base_url='http://test.com')
        assert result['gre_q'] is None


# =============================================================================
# Lines 181-182: Exception in GRE AW parsing
# =============================================================================

@pytest.mark.db
def test_parse_detail_gre_aw_exception():
    """Lines 181-182: Exception handler in GRE AW parsing"""
    from src.module_2_1.scrape import parse_detail_page_html
    
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # HTML with invalid GRE AW value
        mock_get.return_value = '<html><body><div>GRE AW: bad_value</div></body></html>'
        
        result = parse_detail_page_html('http://test.com', base_url='http://test.com')
        assert result['gre_aw'] is None


# =============================================================================
# Lines 190-191: General exception handler in _parse_detail_page_html
# =============================================================================

@pytest.mark.db
def test_parse_detail_general_exception():
    """Lines 190-191: General exception handler"""
    from src.module_2_1.scrape import parse_detail_page_html
    
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # Make _get_html raise an exception
        mock_get.side_effect = Exception("Network error")
        
        result = parse_detail_page_html('http://test.com', base_url='http://test.com')
        # Should return default dict with None values
        assert result['gpa'] is None
        assert result['citizenship'] is None


# =============================================================================
# Line 250: "Wait listed" → "Waitlisted" normalization
# =============================================================================

@pytest.mark.db
def test_parse_row_waitlisted_normalization():
    """Line 250: Normalize 'Wait listed' to 'Waitlisted'"""
    from src.module_2_1.scrape import parse_row
    
    html = '''
    <tr>
        <td><div class="tw-font-medium">Stanford</div><a href="/result/123">Link</a></td>
        <td><div><span>CS</span><span>PhD</span></div></td>
        <td>2024-01-01</td>
        <td>Wait listed on 2024-01-15</td>
    </tr>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    result = parse_row(soup.find('tr'), 'http://base.com')
    
    assert result['status'] == 'Waitlisted'  # Normalized


# =============================================================================
# Line 256: Status match without date
# =============================================================================

@pytest.mark.db
def test_parse_row_status_without_date():
    """Line 256: Parse status without 'on date' format"""
    from src.module_2_1.scrape import parse_row
    
    html = '''
    <tr>
        <td><div class="tw-font-medium">MIT</div><a href="/result/456">Link</a></td>
        <td><div><span>CS</span><span>MS</span></div></td>
        <td>2024-02-01</td>
        <td>Rejected</td>
    </tr>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    result = parse_row(soup.find('tr'), 'http://base.com')
    
    assert result['status'] == 'Rejected'
    assert result['status_date'] is None  # No date provided


# =============================================================================
# Line 312: Progress update during fetch_detail_batch
# =============================================================================

@pytest.mark.db
def test_fetch_detail_batch_progress_update():
    """Line 312: Print progress every 50 items"""
    from src.module_2_1.scrape import fetch_detail_batch
    
    with patch('src.module_2_1.scrape._parse_detail_page_html') as mock_parse:
        mock_parse.return_value = {'gpa': 3.5}
        
        # Create exactly 50 records to trigger progress update
        records = [{'entry_url': f'http://test{i}.com'} for i in range(50)]
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            result = fetch_detail_batch(records, max_workers=2)
            
            # Should have printed progress
            assert any('50/50' in str(call) for call in mock_print.call_args_list)


# =============================================================================
# Line 358: Break when no rows found
# =============================================================================

@pytest.mark.db
def test_scrape_data_no_rows_breaks_loop():
    """Line 358: Break loop when no rows found on page"""
    from src.module_2_1.scrape import scrape_data
    
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # Return HTML with no table rows
        mock_get.return_value = '<html><body><p>No results</p></body></html>'
        
        result = scrape_data(max_entries=100, start_page=1, parallel_threads=1)
        
        # Should return empty or minimal results
        assert isinstance(result, list)


# =============================================================================
# Lines 398-404: Sample entry printing
# =============================================================================

@pytest.mark.db
def test_scrape_data_sample_printing():
    """Lines 398-404: Print sample entries with details"""
    from src.module_2_1.scrape import scrape_data
    
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # Return minimal valid HTML
        mock_get.return_value = '''
        <html><body><table>
            <tr><td><div class="tw-font-medium">Stanford</div><a href="/result/1">L</a></td>
                <td><div><span>CS</span><span>PhD</span></div></td>
                <td>2024-01-01</td>
                <td>Accepted on 2024-01-15</td></tr>
        </table></body></html>
        '''
        
        with patch('src.module_2_1.scrape._parse_detail_page_html') as mock_detail:
            # Return detail with term and GPA to trigger sample printing
            mock_detail.return_value = {
                'term': 'Fall 2024',
                'gpa': 3.8,
                'citizenship': 'American',
                'comments': None,
                'gre_total': 330,
                'gre_v': 165,
                'gre_q': 165,
                'gre_aw': 5.0
            }
            
            result = scrape_data(max_entries=3, start_page=1, parallel_threads=1)
            
            # Should have collected entries
            assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])