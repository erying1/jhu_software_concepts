"""Final routes.py coverage tests."""
import pytest
from unittest.mock import patch, Mock
import subprocess

def test_pull_data_file_write_error(client):
    """Test pull_data when timestamp file write fails."""
    with patch('src.app.routes.subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        with patch('src.app.routes.datetime') as mock_dt:
            mock_now = Mock()
            mock_now.strftime.return_value = "Test Time"
            mock_dt.now.return_value = mock_now
            
            mock_delta = Mock()
            mock_delta.total_seconds.return_value = 60
            type(mock_now).__sub__ = Mock(return_value=mock_delta)
            
            with patch('builtins.open', side_effect=IOError("Cannot write")):
                response = client.post("/pull-data")
                
                # Should complete despite file write error
                assert response.status_code in [200, 302]


def test_analysis_route_with_empty_results(client):
    """Test analysis route when no data exists."""
    with patch('src.app.queries.get_all_results') as mock_results:
        mock_results.return_value = {
            "fall_2026_count": 0,
            "pct_international": 0,
            "avg_metrics": {"avg_gpa": None, "avg_gre": None, "avg_gre_v": None, "avg_gre_aw": None}
        }
        
        response = client.get("/")
        assert response.status_code == 200


def test_pull_data_subprocess_check_true_error(client):
    """Test pull_data with check=True subprocess error."""
    with patch('src.app.routes.subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=2,
            cmd=["python", "scrape.py"]
        )
        
        response = client.post(
            "/pull-data",
            headers={"Accept": "application/json"}
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data or "ok" in data


def test_update_analysis_while_pull_running(client):
    """Test update_analysis is blocked when pull is running."""
    from src.app import routes
    
    original = routes.pull_running
    routes.pull_running = True
    
    try:
        response = client.post("/update-analysis")
        assert response.status_code in [409, 302]
    finally:
        routes.pull_running = original
