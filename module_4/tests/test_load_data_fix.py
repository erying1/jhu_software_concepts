"""
Test for load_data.py lines 39-40
"""
import pytest
import json
import tempfile
import os


@pytest.mark.db
def test_load_json_lines_39_40():
    """Lines 39-40: Successfully load and parse JSON"""
    from src.load_data import load_json
    
    # Create a real temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([{"test": 1}], f)
        temp_path = f.name
    
    try:
        result = load_json(temp_path)
        assert isinstance(result, list)
        assert len(result) == 1
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])