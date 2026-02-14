Testing Guide
=============

This project includes a comprehensive pytest suite with 100% coverage.

Running Tests
-------------

Activate your virtual environment and run:

::

    pytest -q --cov=module_4/src --cov-report=term-missing

Test Categories
---------------

Tests are organized into the following groups:

- **web** — Flask route behavior
- **buttons** — UI-triggered actions
- **analysis** — Dashboard calculations
- **db** — Database insert/query logic
- **integration** — Full end-to-end pipeline
- **scrape / clean / load** — Module 3 ETL components

Mocking Strategy
----------------

The test suite uses:

- `unittest.mock.patch` for subprocess calls
- Mocked database connections for query functions
- Fake file handles for timestamp writes
- JSON fixtures for scraper output

Coverage Requirements
---------------------

The assignment requires:

- 100% test coverage
- No excluded lines
- All branches executed at least once

CI Integration
--------------

A GitHub Actions workflow runs:

- `pytest`
- coverage checks
- Sphinx documentation builds
