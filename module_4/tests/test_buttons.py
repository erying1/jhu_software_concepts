"""
Buttons & Busy-State Behavior Tests
Required by assignment: test_buttons.py

Tests:
1. POST /pull-data returns 200 and triggers loader (mocked)
2. POST /update-analysis returns 200 when not busy
3. POST /update-analysis returns 409 when busy (pull in progress)
4. POST /pull-data returns 409 (or redirect) when already busy
"""
import pytest
from unittest.mock import Mock, patch


@pytest.mark.buttons
def test_pull_data_returns_200_when_not_busy(client):
    """Test POST /pull-data returns 200 and triggers loader (mocked)"""
    # Mock subprocess to avoid actually running scraper/cleaner/loader
    with patch('subprocess.run') as mock_run, \
         patch('builtins.open', create=True) as mock_open:
        
        # Mock file operations
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.write = Mock()
        mock_open.return_value = mock_file
        
        # Mock subprocess calls: not busy check, scraper, cleaner, loader
        mock_run.side_effect = [
            Mock(returncode=0, stdout=b'not busy'),  # Busy check
            Mock(returncode=0, stderr=b''),           # Scraper succeeds
            Mock(returncode=0, stderr=b''),           # Cleaner succeeds
            Mock(returncode=0, stderr=b''),           # Loader succeeds
        ]
        
        response = client.post('/pull-data')
        
        # Should return 200 or 302 (redirect)
        assert response.status_code in [200, 302]
        
        # Verify subprocess was called (loader was triggered)
        assert mock_run.call_count >= 3  # At least scraper, cleaner, loader


@pytest.mark.buttons
def test_update_analysis_returns_200_when_not_busy(client):
    """Test POST /update-analysis returns 200 when not busy"""
    response = client.post('/update-analysis',
                          content_type='application/json',
                          headers={'Accept': 'application/json'})
    
    # Should return 200 when not busy
    assert response.status_code == 200
    
    # Should return JSON
    data = response.get_json()
    assert data is not None


@pytest.mark.buttons
def test_update_analysis_returns_409_when_busy(client):
    """Test POST /update-analysis returns 409 when pull is in progress"""
    from src.app import routes
    
    # Save original state
    original_state = routes.pull_running
    
    try:
        # Set busy state (pull in progress)
        routes.pull_running = True
        
        response = client.post('/update-analysis',
                              content_type='application/json',
                              headers={'Accept': 'application/json'})
        
        # Should return 409 when busy
        assert response.status_code == 409
        
    finally:
        # Restore original state
        routes.pull_running = original_state


@pytest.mark.buttons
def test_pull_data_returns_409_when_busy(client):
    """Test POST /pull-data returns 409 (or appropriate status) when already busy"""
    from src.app import routes
    
    # Save original state
    original_state = routes.pull_running
    
    try:
        # Set busy state
        routes.pull_running = True
        
        with patch('subprocess.run') as mock_run, \
             patch('builtins.open', create=True):
            
            # Mock busy check returning "busy"
            mock_run.return_value = Mock(returncode=1, stdout=b'busy')
            
            response = client.post('/pull-data')
            
            # Should return 409 or 302 (redirect) when already busy
            # (different implementations may vary, but should NOT be 200)
            assert response.status_code in [302, 409]
            assert response.status_code != 200  # Should not succeed when busy
            
    finally:
        # Restore original state
        routes.pull_running = original_state
