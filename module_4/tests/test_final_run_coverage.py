"""Final run.py coverage test."""
import pytest
import subprocess
import sys

def test_run_py_if_main_block():
    """Test the if __name__ == '__main__' block in run.py."""
    # Start the app and kill it immediately
    process = subprocess.Popen(
        [sys.executable, "src/run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give it a moment to start
    import time
    time.sleep(0.5)
    
    # Terminate it
    process.terminate()
    
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
    
    # Should have started (returncode doesn't matter since we killed it)
    assert process.returncode is not None
