import pytest
import src.run as run


@pytest.mark.analysis
def test_run_main(monkeypatch):
    """Test main() starts the server with correct args."""
    calls = {}

    def fake_run(**kwargs):
        calls.update(kwargs)

    monkeypatch.setattr(run.app, "run", fake_run)
    run.main()

    assert calls["host"] == "0.0.0.0"
    assert calls["port"] == 8080
    assert calls["debug"] is True
