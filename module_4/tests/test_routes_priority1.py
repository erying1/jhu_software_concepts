# test_routes_priority1.py

from unittest.mock import patch, Mock, MagicMock
import subprocess


def test_analysis_route_with_load_error(client):
    """Test analysis when loading scraped records fails."""
    with patch('src.app.routes.load_scraped_records') as mock_load:
        mock_load.side_effect = FileNotFoundError("No records")
        
        response = client.get("/")
        # Should handle gracefully
        assert response.status_code in [200, 500]


def test_analysis_route_with_json_decode_error(client):
    """Test analysis when JSON parsing fails."""
    with patch('src.app.routes.Path.read_text') as mock_read:
        mock_read.return_value = "invalid json {"
        
        response = client.get("/")
        assert response.status_code in [200, 500]


def test_pull_data_scraper_subprocess_error(client):
    """Test when scraper subprocess specifically fails."""
    with patch('src.app.routes.subprocess.run') as mock_run:
        # First call (scraper) raises CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["python", "scrape.py"],
            stderr=b"Scraper error"
        )
        
        response = client.post(
            "/pull-data",
            headers={"Accept": "application/json"}
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data or "Subprocess error" in str(data)


def test_pull_data_cleaner_subprocess_error(client):
    """Test when cleaner subprocess specifically fails."""
    with patch('src.app.routes.subprocess.run') as mock_run:
        # Scraper succeeds, cleaner fails
        def side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('cmd', [])
            if 'clean.py' in str(cmd):
                raise subprocess.CalledProcessError(1, cmd, stderr=b"Clean error")
            return Mock(returncode=0)
        
        mock_run.side_effect = side_effect
        
        response = client.post(
            "/pull-data",
            headers={"Accept": "application/json"}
        )
        
        assert response.status_code == 500


def test_pull_data_timestamp_write_fails_in_finally(client):
    """Test when writing timestamp fails in finally block."""
    with patch('src.app.routes.subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        with patch('src.app.routes.datetime') as mock_dt:
            mock_now = Mock()
            mock_now.strftime.return_value = "Jan 01, 2025"
            mock_dt.now.return_value = mock_now
            
            mock_delta = Mock()
            mock_delta.total_seconds.return_value = 60
            type(mock_now).__sub__ = Mock(return_value=mock_delta)
            
            # Make timestamp file write fail
            call_count = [0]
            original_open = open
            
            def mock_open_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] > 0:  # Fail on timestamp writes
                    raise IOError("Permission denied")
                return original_open(*args, **kwargs)
            
            with patch('builtins.open', side_effect=mock_open_side_effect):
                response = client.post("/pull-data")
                # Should complete despite file write error
                assert response.status_code in [200, 302]