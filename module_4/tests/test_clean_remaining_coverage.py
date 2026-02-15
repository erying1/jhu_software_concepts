"""
Tests to cover clean.py lines 239 and 248-255.
"""

import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.module_2_1 import clean


@pytest.mark.analysis
def test_llm_clean_batch_successful_cleanup(monkeypatch, tmp_path):
    """
    Cover line 239: os.remove(tmp_out_path) succeeds.
    
    Previous tests either fail before cleanup or mock os.remove to throw,
    so line 239 (the second os.remove) is never reached. This test lets
    both os.remove calls succeed normally.
    """
    # Create fake input and output files
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "input.json.out"
    input_file.write_text("[]")
    output_file.write_text('{"llm-generated-program": "CS", "llm-generated-university": "MIT"}\n')

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
    monkeypatch.setattr(clean.subprocess, "run", lambda *a, **k: None)
    # Do NOT mock os.remove — let both calls succeed and hit line 239

    records = [{"program_name": "CS", "university": "MIT"}]
    result = clean.llm_clean_batch(records)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["llm-generated-program"] == "CS"
    # Verify both temp files were cleaned up
    assert not input_file.exists()
    assert not output_file.exists()


@pytest.mark.analysis
def test_clean_main_block(monkeypatch):
    """
    Cover lines 248-255: the main() function.
    Calls clean.main() directly with monkeypatched I/O functions.
    """
    fake_raw = [{"program_name": "CS", "university": "MIT"}]
    fake_cleaned = [{"program_name": "CS", "university": "MIT", "status": "Accepted"}]

    saved = {}

    def fake_save(data, path):
        saved["data"] = data
        saved["path"] = path

    monkeypatch.setattr(clean, "load_data", lambda path: fake_raw)
    monkeypatch.setattr(clean, "clean_data", lambda raw: fake_cleaned)
    monkeypatch.setattr(clean, "save_data", fake_save)

    clean.main()

    assert saved["data"] == fake_cleaned
    assert saved["path"] == "module_3/module_2.1/llm_extend_applicant_data.json"
