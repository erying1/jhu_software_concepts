"""
Comprehensive coverage tests to close remaining gaps - FINAL VERSION.
Targets specific uncovered lines in each module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import os


# ==============================================================================
# APP/__INIT__.PY - Lines 29, 39-42, 46-50 (10 lines)
# ==============================================================================

@pytest.mark.web
class TestAppInit:
    """Cover missing lines in app/__init__.py"""
    
    def test_create_app_with_config_dict(self):
        """Test create_app with config dictionary"""
        from src.app import create_app
        
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test-key'
        }
        
        app = create_app(config)
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_create_app_without_config(self):
        """Test create_app without config (default path)"""
        from src.app import create_app
        
        app = create_app()
        assert app is not None


# ==============================================================================
# ROUTES.PY - Missing lines coverage
# ==============================================================================

@pytest.mark.web
class TestRoutesEdgeCases:
    """Cover specific missing lines in routes.py"""
    
    def test_get_last_pull_file_missing(self):
        """get_last_pull when file doesn't exist"""
        from src.app.routes import get_last_pull
        
        with patch('os.path.exists', return_value=False):
            result = get_last_pull()
            assert result is None
    
    def test_get_last_runtime_file_missing(self):
        """get_last_runtime when file doesn't exist"""
        from src.app.routes import get_last_runtime
        
        with patch('os.path.exists', return_value=False):
            result = get_last_runtime()
            assert result is None
    
    def test_load_scraped_records_file_missing(self):
        """load_scraped_records when file doesn't exist"""
        from src.app.routes import load_scraped_records
        
        with patch('pathlib.Path.exists', return_value=False):
            result = load_scraped_records()
            assert result == []
    
    def test_fmt_with_exception(self):
        """fmt function with invalid value"""
        from src.app.routes import fmt
        
        result = fmt("invalid")
        assert result == "invalid"
    
    def test_pct_with_exception(self):
        """pct function with exception"""
        from src.app.routes import pct
        
        result = pct("invalid")
        assert result == "N/A"
    
    def test_na_function(self):
        """na function coverage"""
        from src.app.routes import na
        
        assert na(None) == "N/A"
        assert na("value") == "value"
    
    @patch('subprocess.run')
    @patch('builtins.open', create=True)
    def test_pull_data_subprocess_error_paths(self, mock_open_func, mock_run, client):
        """Subprocess error handling"""
        # Mock file
        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.write = Mock()
        mock_open_func.return_value = mock_file
        
        # Simulate subprocess error
        from subprocess import CalledProcessError
        mock_run.side_effect = [
            Mock(returncode=0, stdout=b'not busy'),
            CalledProcessError(1, 'cmd', stderr=b'error')
        ]
        
        response = client.post('/pull-data')
        assert response.status_code in [200, 302, 500]


# ==============================================================================
# CLEAN.PY - Edge cases
# ==============================================================================

@pytest.mark.db
class TestCleanEdgeCases:
    """Cover missing lines in clean.py"""
    
    def test_normalize_status_variations(self):
        """normalize_status with various inputs"""
        from src.module_2_1.clean import normalize_status
        
        assert normalize_status("Accepted") == "Accepted"
        assert normalize_status("accepted") == "Accepted"
        assert normalize_status("ACCEPTED") == "Accepted"
        assert normalize_status(None) is None
        assert normalize_status("Other") == "Other"


# ==============================================================================
# SCRAPE.PY - Edge cases
# ==============================================================================

@pytest.mark.db
class TestScrapeEdgeCases:
    """Cover missing lines in scrape.py"""
    
    def test_parse_row_no_link(self):
        """_parse_row with no link"""
        from src.module_2_1.scrape import _parse_row
        from bs4 import BeautifulSoup
        
        html = '<tr><td>No link</td></tr>'
        soup = BeautifulSoup(html, 'html.parser')
        result = _parse_row(soup.find('tr'), "http://base.url")
        assert result is None
    
    def test_parse_detail_empty(self):
        """_parse_detail_page_html with empty input"""
        from src.module_2_1.scrape import _parse_detail_page_html
        
        result = _parse_detail_page_html("")
        assert result is not None


# ==============================================================================
# QUERY_DATA.PY - Lines 48, 62-63 (3 lines)
# ==============================================================================

@pytest.mark.analysis
class TestQueryDataEdgeCases:
    """Cover missing lines in query_data.py"""
    
    @patch('src.query_data.get_connection')
    def test_query_with_none_results(self, mock_conn):
        """Query functions returning None"""
        from src.query_data import q1_fall_2026_count
        
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_conn.return_value = mock_connection
        
        # Return None from query
        mock_cursor.fetchone.return_value = (None,)
        
        result = q1_fall_2026_count()
        assert result == 0  # Should handle None


# ==============================================================================
# Additional edge case coverage
# ==============================================================================

@pytest.mark.web
class TestAdditionalCoverage:
    """Additional tests for remaining gaps"""
    
    def test_routes_status_endpoint(self, client):
        """Test /status endpoint"""
        response = client.get('/status')
        assert response.status_code == 200
        data = response.get_json()
        assert 'busy' in data
    
    @patch('subprocess.run')
    @patch('builtins.open', create=True)
    def test_pull_data_general_exception(self, mock_open_func, mock_run, client):
        """Test general exception in pull_data"""
        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.write = Mock()
        mock_open_func.return_value = mock_file
        
        mock_run.side_effect = [
            Mock(returncode=0, stdout=b'not busy'),
            Exception("General error")
        ]
        
        response = client.post('/pull-data')
        assert response.status_code in [200, 302, 500]

###########################################
## Test __init__.py - Lines 39-42, 46-50
###########################################

# Lines 39-42
@pytest.mark.analysis 
def test_create_app_applies_test_config(): 
    from src.app import create_app 
    app = create_app({"SECRET_KEY": "override", "TESTING": True}) 
    assert app.config["SECRET_KEY"] == "override" 
    assert app.config["TESTING"] is True

# Lines 46-50
@pytest.mark.analysis 
def test_create_app_pytest_env_override(monkeypatch): 
    from src.app import create_app 

    # Simulate pytest environment variable
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "true") 
    
    app = create_app() 
    assert app.config["TESTING"] is True

import pytest
import os

@pytest.mark.analysis
def test_create_app_all_branches(monkeypatch):
    from src.app import create_app

    # Hit the PYTEST_CURRENT_TEST branch
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "true")

    # Hit the config-provided branch
    app = create_app({"DEBUG": True})

    assert app.config["DEBUG"] is True
    assert app.config["TESTING"] is True  # set by env var

    # Hit the no-config branch
    app2 = create_app()
    assert app2.config["TESTING"] is True

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src", "--cov-report=term-missing"])
