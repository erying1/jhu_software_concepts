"""
Tests specifically targeting app/__init__.py lines 39-42, 46-50
"""
import pytest


@pytest.mark.web
def test_pct_filter_exception_handler():
    """Lines 39-42: pct_filter exception handler when value cannot be converted to float"""
    from src.app import create_app
    
    app = create_app()
    
    # Get the pct filter
    pct_filter = app.jinja_env.filters['pct']
    
    # Test the exception path - pass something that can't be converted to float
    result = pct_filter("not a number")
    assert result == "0.00"
    
    # Also test with None
    result2 = pct_filter(None)
    assert result2 == "0.00"


@pytest.mark.web
def test_na_filter_empty_string_check():
    """Lines 46-50: na_filter checks for None and empty strings"""
    from src.app import create_app
    
    app = create_app()
    
    # Get the na filter
    na_filter = app.jinja_env.filters['na']
    
    # Line 46-47: None case
    result = na_filter(None)
    assert result == "N/A"
    
    # Lines 48-49: Empty string case
    result2 = na_filter("   ")  # String with only whitespace
    assert result2 == "N/A"
    
    result3 = na_filter("")  # Empty string
    assert result3 == "N/A"
    
    # Line 50: Return value as-is
    result4 = na_filter("some value")
    assert result4 == "some value"
    
    result5 = na_filter(42)
    assert result5 == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])