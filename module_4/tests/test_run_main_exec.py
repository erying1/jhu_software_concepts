import pytest
import src.run as run


@pytest.mark.analysis
def test_run_main_executes():
    """Ensure _run_main returns the expected coverage-safe value."""
    result = run._run_main()
    assert result == "run_main_executed"


@pytest.mark.analysis
def test_run_server_returns_callable():
    """Ensure _run_server returns something callable (Flask's bound method)."""
    run_fn = run._run_server()
    assert callable(run_fn)


@pytest.mark.analysis
def test_main_block_indirect(monkeypatch):
    """
    Indirectly test the __main__ block by calling the server wrapper
    and ensuring our monkeypatched run() is invoked.
    """
    calls = {}

    def fake_run(*args, **kwargs):
        calls["called"] = True

    # Patch the Flask app.run method
    monkeypatch.setattr(run.app, "run", fake_run)

    # Call the wrapper exactly as the __main__ block would
    run._run_server()(host="0.0.0.0", port=8080, debug=True)

    assert calls.get("called") is True

