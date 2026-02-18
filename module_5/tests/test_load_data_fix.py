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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
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


@pytest.mark.db
def test_load_json_real_open(tmp_path):
    """Covers the real open() path in load_json."""
    from src.load_data import load_json

    file = tmp_path / "data.json"
    file.write_text('[{"a": 1}]')

    result = load_json(str(file))
    assert result == [{"a": 1}]


@pytest.mark.db
def test_main_returns_expected_value(monkeypatch):
    from src import load_data

    monkeypatch.setattr(load_data, "load_into_db", lambda filepath: None)
    assert load_data.main() == "load_data_main_executed"
