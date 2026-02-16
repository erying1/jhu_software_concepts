"""Tests for load_data.py cli_main() — argument parsing branches."""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.db
def test_cli_main_default_no_drop(monkeypatch):
    """cli_main without --drop calls main(drop=False)."""
    from src import load_data

    called_with = {}

    def fake_main(drop=False):
        called_with["drop"] = drop
        return "ok"

    monkeypatch.setattr(load_data, "main", fake_main)
    load_data.cli_main([])  # no args = no --drop

    assert called_with["drop"] is False


@pytest.mark.db
def test_cli_main_with_drop_flag(monkeypatch):
    """cli_main with --drop calls main(drop=True)."""
    from src import load_data

    called_with = {}

    def fake_main(drop=False):
        called_with["drop"] = drop
        return "ok"

    monkeypatch.setattr(load_data, "main", fake_main)
    load_data.cli_main(["--drop"])

    assert called_with["drop"] is True
