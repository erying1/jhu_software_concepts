# Fix for tests/conftest.py
# This ensures TESTING is properly set

import sys
import os
import pytest
from pathlib import Path

# Ensure .env exists for coverage BEFORE any imports
# (run.py loads it at import time, so must exist before conftest imports anything)
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
env_example = project_root / ".env.example"

if not env_file.exists() and env_example.exists():
    env_file.write_text(env_example.read_text())

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import create_app


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing (persistent across requests)."""
    app = create_app()
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_applicant_data():
    return [
        {
            "program": "CS PhD",
            "comments": "Test",
            "date_added": "2024-01-01",
            "url": "http://example.com/1",
            "status": "Accepted",
            "status_date": "2024-01-02",
            "term": "Fall 2026",
            "us_or_international": "American",
            "gpa": 3.8,
            "gre_total_score": 320,
            "gre_verbal_score": 160,
            "gre_aw_score": 4.5,
            "degree": "PhD",
            "llm_generated_program": "Computer Science",
            "llm_generated_university": "MIT",
        }
    ]
