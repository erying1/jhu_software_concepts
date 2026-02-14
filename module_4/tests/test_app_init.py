# tests/test_app_init.py

def test_format_percentage_with_invalid_input():
    """Test percentage filter with invalid input."""
    from src.app import create_app
    
    app = create_app()
    
    with app.app_context():
        pct_filter = app.jinja_env.filters['pct']
        
        # Test with None
        assert pct_filter(None) == "0.00"
        
        # Test with invalid string
        assert pct_filter("invalid") == "0.00"
        
        # Test with empty string
        assert pct_filter("") == "0.00"


def test_format_na_with_various_inputs():
    """Test na filter edge cases."""
    from src.app import create_app
    
    app = create_app()
    
    with app.app_context():
        na_filter = app.jinja_env.filters['na']
        
        # Already covered cases
        assert na_filter(None) == "N/A"
        assert na_filter("") == "N/A"
        assert na_filter("  ") == "N/A"
        
        # Valid values should pass through
        assert na_filter("test") == "test"
        assert na_filter(123) == 123