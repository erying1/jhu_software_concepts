"""Tests for scrape.py cli_main() — all three branches."""

import pytest
from unittest.mock import patch


@pytest.mark.web
def test_cli_main_success(monkeypatch):
    """cli_main prints elapsed time on success."""
    from src.module_2_1 import scrape

    monkeypatch.setattr(scrape, "main", lambda: None)
    scrape.cli_main()  # should print timing without error


@pytest.mark.web
def test_cli_main_keyboard_interrupt(monkeypatch, capsys):
    """cli_main handles KeyboardInterrupt gracefully."""
    from src.module_2_1 import scrape

    def raise_interrupt():
        raise KeyboardInterrupt()

    monkeypatch.setattr(scrape, "main", raise_interrupt)
    scrape.cli_main()

    output = capsys.readouterr().out
    assert "Interrupted by user" in output


@pytest.mark.web
def test_cli_main_exception(monkeypatch, capsys):
    """cli_main handles unexpected exceptions and prints traceback."""
    from src.module_2_1 import scrape

    def raise_error():
        raise RuntimeError("test failure")

    monkeypatch.setattr(scrape, "main", raise_error)
    scrape.cli_main()

    output = capsys.readouterr().out
    assert "Error: test failure" in output
