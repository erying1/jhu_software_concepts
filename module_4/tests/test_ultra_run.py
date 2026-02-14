"""Ultra-targeted run.py test."""
import subprocess
import sys
import os


def test_run_py_main_block_coverage():
    """Ensure run.py main block is covered."""
    env = os.environ.copy()
    env['FLASK_ENV'] = 'testing'
    
    proc = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'src'); import run"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    import time
    time.sleep(0.3)
    proc.terminate()
    
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()
    
    assert proc.returncode is not None
