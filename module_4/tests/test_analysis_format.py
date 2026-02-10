"""Analysis formatting tests"""
import pytest
import re

@pytest.mark.analysis
def test_percentages_have_two_decimals(client):
    """Test that percentages are formatted with 2 decimals"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Find all percentages in the page
    percentages = re.findall(r'\d+\.\d+%', html)
    
    # Check each has exactly 2 decimal places
    for pct in percentages:
        decimal_part = pct.split('.')[1].rstrip('%')
        assert len(decimal_part) == 2, f"Expected 2 decimals, got: {pct}"

@pytest.mark.analysis
def test_analysis_has_labels(client):
    """Test analysis items are labeled"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'Answer:' in html or 'Q' in html
