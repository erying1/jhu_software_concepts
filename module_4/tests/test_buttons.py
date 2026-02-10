"""Button behavior tests"""
import pytest
import json

@pytest.mark.buttons
def test_pull_data_endpoint_exists(client, mocker):
    """Test POST /pull-data endpoint exists"""
    # Mock subprocess to avoid actually running scraper
    mocker.patch('subprocess.run')
    mocker.patch('builtins.open', mocker.mock_open())
    
    response = client.post('/pull-data')
    # Should not be 404
    assert response.status_code != 404

@pytest.mark.buttons  
def test_update_analysis_endpoint_exists(client):
    """Test POST /update-analysis endpoint exists"""
    response = client.post('/update-analysis')
    assert response.status_code != 404