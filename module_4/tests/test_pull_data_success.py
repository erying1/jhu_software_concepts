# test_pull_data_success
# Mock subprocess.run, datetime, and file I/O

from unittest.mock import patch
from src.app import routes

def test_pull_data_success(client):
    with patch('subprocess.run'), \
         patch('src.app.routes.datetime'), \
         patch('builtins.open'):
        response = client.post("/pull-data")
        assert response.status_code in [200, 302]
