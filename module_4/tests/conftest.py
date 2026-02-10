"""Pytest configuration and shared fixtures"""
import pytest
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def app():
    """Create Flask app for testing"""
    from src.app import create_app
    test_config = {
        'TESTING': True,
        'DATABASE_URL': os.getenv('TEST_DATABASE_URL', 'postgresql://localhost/gradcafe_test'),
        'SECRET_KEY': 'test-secret-key',
    }
    app = create_app(test_config)
    yield app

@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()

@pytest.fixture
def sample_applicant_data():
    """Sample test data"""
    return [
        {
            "program_name": "Computer Science",
            "university": "Stanford University",
            "date_added": "2026-01-15",
            "entry_url": "https://www.thegradcafe.com/result/test001",
            "status": "Accepted",
            "status_date": "15 Jan",
            "degree_level": "PhD",
            "comments": "Great program!",
            "term": "Fall 2026",
            "citizenship": "International",
            "gpa": 3.9,
            "gre_total": 330,
            "gre_v": 165,
            "gre_q": 165,
            "gre_aw": 5.0,
            "llm-generated-program": "Computer Science",
            "llm-generated-university": "Stanford University"
        }
    ]
