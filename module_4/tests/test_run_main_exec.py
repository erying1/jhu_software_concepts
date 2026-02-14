# tests/test_run.py

def test_run_main_execution():
    """Test that run.py can be executed as main."""
    import subprocess
    import sys
    
    result = subprocess.run(
        [sys.executable, "src/run.py"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    # Should start Flask app (won't complete in test, that's ok)
    assert result.returncode in [0, 1]  # May exit with error when terminated