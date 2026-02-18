Testing Guide
=============

This project includes a comprehensive pytest suite with 100% statement coverage.

Running Tests
-------------

Activate your virtual environment and run the full suite::

    pytest -m "web or buttons or analysis or db or integration"

This executes all marked tests. Coverage is enforced automatically via ``pytest.ini``::

    [pytest]
    addopts = -q --cov=src --cov-report=term-missing --cov-fail-under=100

Test Markers
------------

Every test is marked with at least one of:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Marker
     - What it covers
   * - ``@pytest.mark.web``
     - Flask page load, HTML structure, route existence
   * - ``@pytest.mark.buttons``
     - ``/pull-data`` and ``/update-analysis`` endpoints, busy-state 409 responses
   * - ``@pytest.mark.analysis``
     - "Answer:" labels, two-decimal percentage formatting, data cleaning
   * - ``@pytest.mark.db``
     - Database inserts, duplicate rejection, schema validation, query functions
   * - ``@pytest.mark.integration``
     - End-to-end: pull → update → render with correctly formatted values

Run a single group::

    pytest -m db
    pytest -m "web or buttons"

No unmarked tests exist. The union of all five markers equals the full suite.

Stable Selectors
-----------------

The analysis template uses ``data-testid`` attributes for reliable test assertions:

- ``data-testid="pull-data-btn"`` — the "Pull Data" button
- ``data-testid="update-analysis-btn"`` — the "Update Analysis" button

Tests use BeautifulSoup to parse HTML and locate these selectors.

Test Fixtures & Doubles
-----------------------

The suite uses these mocking strategies:

**Database** — ``src.query_data.get_connection`` is patched to return an
in-memory or test-scoped PostgreSQL connection. The ``applicants`` table is
created fresh in each test that needs it.

**Subprocess** — ``subprocess.run`` is patched in route tests so
``/pull-data`` never spawns real scraper/cleaner/loader processes.

**File I/O** — Timestamp files (``last_pull.txt``, ``last_runtime.txt``) and
JSON data files are mocked via ``monkeypatch`` or ``tmp_path``.

**Scraper** — Tests inject a fake scraper that returns deterministic records
without hitting the network. No test depends on live internet access.

Key Test Files
--------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - File
     - What it tests
   * - ``test_flask_page.py``
     - App factory, GET /analysis 200, buttons present, "Answer:" labels
   * - ``test_buttons.py``
     - POST /pull-data and /update-analysis success + 409 busy gating
   * - ``test_analysis_format.py``
     - "Answer" labels rendered, percentages have two decimals
   * - ``test_db_insert.py``
     - Insert creates rows, duplicates rejected, query returns dict, schema check
   * - ``test_integration_end_to_end.py``
     - Full pipeline pull→update→render, multi-pull uniqueness

Coverage Requirements
---------------------

- 100% statement coverage enforced via ``--cov-fail-under=100``
- ``# pragma: no cover`` is used only on ``if __name__ == "__main__"`` guards
  (standard Python convention for untestable CLI entry points)
- All other code paths are exercised by the test suite
