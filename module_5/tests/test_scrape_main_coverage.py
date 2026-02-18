"""
Tests to cover scrape.py main() function (lines ~400-424).
"""

import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.module_2_1 import scrape


@pytest.mark.analysis
def test_scrape_main_robots_fail(monkeypatch):
    """Cover main() when robots check fails."""
    monkeypatch.setattr(scrape, "check_robots", lambda: False)

    with pytest.raises(SystemExit, match="robots.txt"):
        scrape.main()


@pytest.mark.analysis
def test_scrape_main_success(monkeypatch, tmp_path):
    """Cover main() full happy path — scrape, makedirs, save JSON."""
    monkeypatch.setattr(scrape, "check_robots", lambda: True)
    monkeypatch.setattr(
        scrape,
        "scrape_data",
        lambda max_entries, start_page, parallel_threads: [
            {"program_name": "CS", "university": "MIT"}
        ],
    )

    # chdir so the relative paths inside main() land in tmp_path
    monkeypatch.chdir(tmp_path)

    scrape.main()

    output_file = tmp_path / "module_3" / "module_2.1" / "raw_applicant_data.json"
    assert output_file.exists()
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["program_name"] == "CS"
