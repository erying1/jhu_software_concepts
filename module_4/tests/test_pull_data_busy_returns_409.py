# test_pull_data_busy_returns_409
# Just set a flag, test, reset - no subprocess mocking needed!

from src.app import routes 

def test_pull_data_busy_returns_409(client):
    routes.pull_running = True
    response = client.post(
        "/pull-data",
        json={}, # forces JSON mode
        headers={"Accept": "application/json"}
    )
    assert response.status_code == 409
    routes.pull_running = False
