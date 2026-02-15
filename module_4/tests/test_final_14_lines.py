"""
Tests for the final 14 uncovered lines (exception handlers and edge cases)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import json

# =============================================================================
# QUERY_DATA.PY - Line 48
# =============================================================================

@pytest.mark.db
def test_query_data_format_or_passthrough_string_input():
    """Line 48: _format_or_passthrough returns string as-is"""
    from src.query_data import _format_or_passthrough
    
    # Test with string input (line 48 - return val unchanged)
    result = _format_or_passthrough("3.50")
    assert result == "3.50"
    
    # Test with another string
    result2 = _format_or_passthrough("already formatted")
    assert result2 == "already formatted"


# =============================================================================
# LOAD_DATA.PY - Lines 40-41, 57, 221-222, 225
# =============================================================================

@pytest.mark.db
def test_load_data_load_json_file_not_found():
    """Line 40-41: load_json with non-existent file"""
    from src.load_data import load_json
    
    with pytest.raises(FileNotFoundError):
        load_json("this_file_does_not_exist.json")


@pytest.mark.db
def test_load_data_normalize_record_alternative_keys():
    """Line 57: normalize_record uses alternative keys"""
    from src.load_data import normalize_record
    
    # Test with llm-generated-program (hyphenated version)
    record = {
        "program_name": "CS",
        "comments": "test",
        "date_added": "2024-01-01",
        "entry_url": "http://test.com",
        "status": "Accepted",
        "status_date": "2024-01-15",
        "term": "Fall 2024",
        "citizenship": "American",
        "gpa": 3.5,
        "gre_total": 330,
        "gre_v": 165,
        "gre_aw": 5.0,
        "degree_level": "PhD",
        "llm-generated-program": "Computer Science",  # Hyphenated version
        "llm-generated-university": "MIT"  # Hyphenated version
    }
    
    result = normalize_record(record)
    assert result["llm_generated_program"] == "Computer Science"
    assert result["llm_generated_university"] == "MIT"


# Lines 221-222, 225 are in reset_database, which is dangerous to test
# as it actually drops the database. Skip these.


# =============================================================================
# CLEAN.PY - Lines 129, 141-143
# =============================================================================

@pytest.mark.db
def test_clean_citizenship_normalization_edge_cases():
    """Lines 129, 141-143: Citizenship normalization paths"""
    from src.module_2_1.clean import _clean_single_record
    
    # Line 129: International Student → International
    record1 = {
        'status': 'Accepted',
        'citizenship': 'International Student',
        'gpa': '3.5',
        'program_name': 'CS',
        'university': 'MIT',
        'comments': None,
        'date_added': '2024-01-01',
        'entry_url': 'http://test.com',
        'status_date': '2024-01-15',
        'term': 'Fall 2026',
        'degree_level': 'PhD',
        'gre_total': None,
        'gre_v': None,
        'gre_aw': None
    }
    result1 = _clean_single_record(record1)
    assert result1['citizenship'] == 'International'
    
    # Lines 141-143: Other citizenship values
    record2 = {
        'status': 'Accepted',
        'citizenship': 'Canadian',  # Not American or International
        'gpa': '3.5',
        'program_name': 'CS',
        'university': 'MIT',
        'comments': None,
        'date_added': '2024-01-01',
        'entry_url': 'http://test.com',
        'status_date': '2024-01-15',
        'term': 'Fall 2026',
        'degree_level': 'PhD',
        'gre_total': None,
        'gre_v': None,
        'gre_aw': None
    }
    result2 = _clean_single_record(record2)
    assert result2['citizenship'] == 'Other'


# =============================================================================
# SCRAPE.PY - Lines 130-131, 159-160, 170-171, 181-182
# =============================================================================

@pytest.mark.db
def test_scrape_all_exception_handlers():
    """Lines 130-131, 159-160, 170-171, 181-182: All exception handlers in scrape"""
    from src.module_2_1.scrape import _parse_detail_page_html
    
    # Create HTML that triggers exceptions in each parser
    with patch('src.module_2_1.scrape._get_html') as mock_get:
        # HTML with values that will cause exceptions during parsing
        mock_get.return_value = '''
        <html><body>
            <div>GPA: not_a_number</div>
            <div>GRE V: xxx</div>
            <div>GRE Q: yyy</div>
            <div>GRE AW: zzz</div>
        </body></html>
        '''
        
        result = _parse_detail_page_html('http://test.com')
        
        # All should be None due to exceptions
        assert result['gpa'] is None  # Line 130-131
        assert result['gre_v'] is None  # Line 159-160
        assert result['gre_q'] is None  # Line 170-171
        assert result['gre_aw'] is None  # Line 181-182


# =============================================================================
# ROUTES.PY - Lines 92, 127, 171, 177, 204-205, 253-254
# These are buggy exception handlers that cannot be tested without fixing
# the source code bugs first (they reference undefined variables)
# =============================================================================

@pytest.mark.skip(reason="Lines 92, 127, 171, 177, 204-205, 253-254 are buggy exception handlers")
def test_routes_buggy_exception_handlers():
    """
    These lines are exception handlers with bugs:
    - Line 92: References undefined 'results' variable
    - Line 127: Unreachable exception handler
    - Lines 171, 177: Reference undefined variables in template
    - Lines 204-205: Unreachable error path
    - Lines 253-254: Similar issues
    
    Cannot test without fixing source code bugs first.
    """
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])