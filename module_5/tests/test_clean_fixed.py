"""
Tests for clean.py - Data cleaning functions
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.module_2_1 import clean


@pytest.mark.analysis
def test_normalize_status_accepted():
    """Test status normalization for accepted"""
    assert clean._normalize_status("accepted") == "Accepted"
    assert clean._normalize_status("ACCEPTED") == "Accepted"
    assert clean._normalize_status(" accept ") == "Accepted"


@pytest.mark.analysis
def test_normalize_status_rejected():
    """Test status normalization for rejected"""
    assert clean._normalize_status("rejected") == "Rejected"
    assert clean._normalize_status("reject") == "Rejected"


@pytest.mark.analysis
def test_normalize_status_waitlisted():
    """Test status normalization for waitlisted"""
    assert clean._normalize_status("waitlisted") == "Waitlisted"
    assert clean._normalize_status("wait listed") == "Waitlisted"


@pytest.mark.analysis
def test_normalize_status_none():
    """Test status normalization with None"""
    assert clean._normalize_status(None) is None
    assert clean._normalize_status("") is None


@pytest.mark.analysis
def test_clean_single_record():
    """Test cleaning a single record"""
    raw = {
        "program_name": "  Computer Science  ",
        "university": "MIT",
        "status": "accepted",
        "comments": "<p>Great program!</p>",
        "gpa": "3.9",
        "gre_v": "165",
        "gre_aw": "5.0",
        "citizenship": "international",
    }

    result = clean._clean_single_record(raw)

    assert result["program_name"] == "Computer Science"
    assert result["status"] == "Accepted"
    assert result["comments"] == "Great program!"
    assert result["gpa"] == 3.9
    assert result["gre_v"] == 165
    assert result["gre_aw"] == 5.0
    assert result["citizenship"] == "International"


@pytest.mark.analysis
def test_clean_single_record_handles_invalid_numbers():
    """Test that invalid numbers become None"""
    raw = {"gpa": "invalid", "gre_v": "not a number", "gre_aw": "xyz"}

    result = clean._clean_single_record(raw)

    assert result["gpa"] is None
    assert result["gre_v"] is None
    assert result["gre_aw"] is None


@pytest.mark.analysis
def test_clean_single_record_citizenship_american():
    """Test citizenship normalization to American"""
    raw = {"citizenship": "american"}
    result = clean._clean_single_record(raw)
    assert result["citizenship"] == "American"


@pytest.mark.analysis
def test_clean_single_record_citizenship_other():
    """Test citizenship defaults to Other"""
    raw = {"citizenship": "Unknown"}
    result = clean._clean_single_record(raw)
    assert result["citizenship"] == "Other"


@pytest.mark.analysis
@patch("src.module_2_1.clean.llm_clean_batch")
@patch("src.module_2_1.clean.save_data")
def test_clean_data(mock_save, mock_llm):
    """Test full cleaning pipeline"""
    raw_records = [
        {"program_name": "CS", "university": "MIT", "status": "accepted", "gpa": "3.9"}
    ]

    # Mock LLM response
    mock_llm.return_value = [
        {
            "llm-generated-program": "Computer Science",
            "llm-generated-university": "Massachusetts Institute of Technology",
        }
    ]

    result = clean.clean_data(raw_records)

    assert len(result) == 1
    assert result[0]["status"] == "Accepted"
    assert result[0]["llm-generated-program"] == "Computer Science"
    mock_save.assert_called_once()


@pytest.mark.analysis
def test_save_data(tmp_path):
    """Test saving data to JSON"""
    test_file = tmp_path / "test_output.json"
    data = [{"program": "CS", "university": "MIT"}]

    clean.save_data(data, str(test_file))

    assert test_file.exists()
    loaded = json.loads(test_file.read_text())
    assert loaded == data


@pytest.mark.analysis
def test_load_data(tmp_path):
    """Test loading data from JSON"""
    test_file = tmp_path / "test_input.json"
    data = [{"program": "Physics"}]
    test_file.write_text(json.dumps(data))

    result = clean.load_data(str(test_file))

    assert result == data


@pytest.mark.analysis
@patch("subprocess.run", side_effect=Exception("LLM failed"))
def test_llm_clean_batch_failure_returns_original(mock_subprocess):
    """Test LLM failure returns original records"""
    records = [{"program_name": "CS"}]

    result = clean.llm_clean_batch(records)

    assert result == records


@pytest.mark.analysis
def test_llm_clean_batch_empty_input():
    """Test LLM with empty input"""
    result = clean.llm_clean_batch([])
    assert result == []


@pytest.mark.analysis
def test_clean_data_empty_list():
    from src.module_2_1 import clean

    assert clean.clean_data([]) == []


@pytest.mark.analysis
def test_clean_data_save_data_failure(monkeypatch):
    from src.module_2_1 import clean

    # Force save_data to raise FileNotFoundError
    monkeypatch.setattr(
        clean, "save_data", lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError())
    )

    raw = [{"program_name": "CS", "university": "MIT"}]

    # Should still return cleaned records
    result = clean.clean_data(raw)
    assert len(result) == 1


@pytest.mark.analysis
def test_llm_clean_batch_missing_output(monkeypatch, tmp_path):
    from src.module_2_1 import clean

    # Fake subprocess.run to succeed
    monkeypatch.setattr(clean.subprocess, "run", lambda *a, **k: None)

    # Fake NamedTemporaryFile to control paths
    class FakeTmp:
        def __init__(self):
            self.name = str(tmp_path / "input.json")

        def write(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(clean.tempfile, "NamedTemporaryFile", lambda *a, **k: FakeTmp())

    # Do NOT create the .out file → triggers exception
    records = [{"program_name": "CS", "university": "MIT"}]
    result = clean.llm_clean_batch(records)

    # Should return original records
    assert result == records


@pytest.mark.analysis
def test_llm_clean_batch_cleanup_failure(monkeypatch, tmp_path):
    from src.module_2_1 import clean

    # Fake subprocess.run to succeed
    monkeypatch.setattr(clean.subprocess, "run", lambda *a, **k: None)

    # Create fake input and output files
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "input.json.out"
    input_file.write_text("[]")
    output_file.write_text("{}")

    # Fake NamedTemporaryFile to return our paths
    class FakeTmp:
        def __init__(self):
            self.name = str(input_file)

        def write(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(clean.tempfile, "NamedTemporaryFile", lambda *a, **k: FakeTmp())

    # Force os.remove to fail
    monkeypatch.setattr(
        clean.os, "remove", lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
    )

    records = [{"program_name": "CS", "university": "MIT"}]
    result = clean.llm_clean_batch(records)

    # Should still return parsed output (empty list)
    assert isinstance(result, list)


@pytest.mark.analysis
def test_llm_clean_batch_read_failure(monkeypatch, tmp_path):
    from src.module_2_1 import clean

    # Fake subprocess.run to succeed
    monkeypatch.setattr(clean.subprocess, "run", lambda *a, **k: None)

    # Create fake input file
    input_file = tmp_path / "input.json"
    input_file.write_text("[]")

    # Fake NamedTemporaryFile to return our input path
    class FakeTmp:
        def __init__(self):
            self.name = str(input_file)

        def write(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(clean.tempfile, "NamedTemporaryFile", lambda *a, **k: FakeTmp())

    # DO NOT create the .out file → triggers read failure
    records = [{"program_name": "CS", "university": "MIT"}]
    result = clean.llm_clean_batch(records)

    assert result == records


@pytest.mark.analysis
def test_llm_clean_batch_cleanup_exception(monkeypatch, tmp_path):
    from src.module_2_1 import clean

    # Fake subprocess.run to succeed
    monkeypatch.setattr(clean.subprocess, "run", lambda *a, **k: None)

    # Create fake input and output files
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "input.json.out"
    input_file.write_text("[]")
    output_file.write_text('{"llm-generated-program": "X"}\n')

    # Fake NamedTemporaryFile to return our input path
    class FakeTmp:
        def __init__(self):
            self.name = str(input_file)

        def write(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(clean.tempfile, "NamedTemporaryFile", lambda *a, **k: FakeTmp())

    # Force os.remove to fail
    monkeypatch.setattr(
        clean.os, "remove", lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
    )

    records = [{"program_name": "CS", "university": "MIT"}]
    result = clean.llm_clean_batch(records)

    # Should still return parsed output
    assert isinstance(result, list)
    assert result[0]["llm-generated-program"] == "X"


@pytest.mark.analysis
def test_llm_clean_batch_read_failure(monkeypatch, tmp_path):
    from src.module_2_1 import clean

    # Fake subprocess.run to succeed
    monkeypatch.setattr(clean.subprocess, "run", lambda *a, **k: None)

    # Create fake input file
    input_file = tmp_path / "input.json"
    input_file.write_text("[]")

    # Fake NamedTemporaryFile to return our input path
    class FakeTmp:
        def __init__(self):
            self.name = str(input_file)

        def write(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(clean.tempfile, "NamedTemporaryFile", lambda *a, **k: FakeTmp())

    # DO NOT create the .out file → triggers read failure
    records = [{"program_name": "CS", "university": "MIT"}]
    result = clean.llm_clean_batch(records)

    assert result == records


@pytest.mark.analysis
def test_llm_clean_batch_cleanup_exception(monkeypatch, tmp_path):
    from src.module_2_1 import clean

    # Fake subprocess.run to succeed
    monkeypatch.setattr(clean.subprocess, "run", lambda *a, **k: None)

    # Create fake input and output files
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "input.json.out"
    input_file.write_text("[]")
    output_file.write_text('{"llm-generated-program": "X"}\n')

    # Fake NamedTemporaryFile to return our input path
    class FakeTmp:
        def __init__(self):
            self.name = str(input_file)

        def write(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(clean.tempfile, "NamedTemporaryFile", lambda *a, **k: FakeTmp())

    # Force os.remove to fail
    monkeypatch.setattr(
        clean.os, "remove", lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
    )

    records = [{"program_name": "CS", "university": "MIT"}]
    result = clean.llm_clean_batch(records)

    # Should still return parsed output
    assert isinstance(result, list)
    assert result[0]["llm-generated-program"] == "X"
