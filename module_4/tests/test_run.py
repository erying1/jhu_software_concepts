"""
Tests for run.py - Application entry point
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.mark.integration
@patch('src.app.create_app')
def test_run_py_imports(mock_create_app):
    """Test that run.py can be imported"""
    mock_app = Mock()
    mock_create_app.return_value = mock_app
    
    # Import run.py
    import src.run as run_module
    
    # Should have created an app
    assert run_module.app is not None


@pytest.mark.integration
def test_flask_app_exists(app):
    """Test that Flask app exists and is configured"""
    assert app is not None
    assert app.config['TESTING'] is True
