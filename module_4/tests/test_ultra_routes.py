"""Ultra-targeted routes.py tests."""
import pytest
from unittest.mock import patch, Mock
import subprocess


def test_pull_data_first_subprocess_fails(client):
    """Test pull_data when first subprocess (scraper) fails."""
    with patch('src.app.routes.subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["python", "scrape.py"]
        )
        
        response = client.post(
            "/pull-data",
            headers={"Accept": "application/json"}
        )
        
        assert response.status_code == 500


def test_pull_data_second_subprocess_fails(client):
    """Test pull_data when second subprocess (cleaner) fails."""
    with patch('src.app.routes.subprocess.run') as mock_run:
        mock_run.side_effect = [
            Mock(returncode=0),
            subprocess.CalledProcessError(returncode=1, cmd=["python", "clean.py"])
        ]
        
        response = client.post(
            "/pull-data",
            headers={"Accept": "application/json"}
        )
        
        assert response.status_code == 500


def test_pull_data_third_subprocess_fails(client):
    """Test pull_data when third subprocess (loader) fails."""
    with patch('src.app.routes.subprocess.run') as mock_run:
        mock_run.side_effect = [
            Mock(returncode=0),
            Mock(returncode=0),
            subprocess.CalledProcessError(returncode=1, cmd=["python", "load_data.py"])
        ]
        
        response = client.post(
            "/pull-data",
            headers={"Accept": "application/json"}
        )
        
        assert response.status_code == 500


def test_status_endpoint(client):
    """Test /status endpoint returns busy state."""
    response = client.get("/status")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "busy" in data
    assert isinstance(data["busy"], bool)
