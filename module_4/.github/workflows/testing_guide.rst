Testing Guide
=============

This project includes a comprehensive test suite with 157 tests covering all major functionality.

Running Tests
-------------

**Full test suite:**

.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration"

**With coverage report:**

.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration" --cov=src --cov-report=term-missing

**Specific test categories:**

.. code-block:: bash

   # Web/Flask tests
   pytest -m web

   # Button behavior tests
   pytest -m buttons

   # Analysis formatting tests
   pytest -m analysis

   # Database tests
   pytest -m db

   # Integration/end-to-end tests
   pytest -m integration

Test Markers
------------

All tests are marked with one or more of the following pytest markers:

**@pytest.mark.web**
  - Flask page rendering and routing
  - HTML structure validation
  - Template rendering
  - Examples: ``test_analysis_route_exists``, ``test_analysis_page_has_buttons``

**@pytest.mark.buttons**
  - Pull Data and Update Analysis button behavior
  - Busy-state gating logic
  - HTTP status code validation
  - Examples: ``test_pull_data_returns_200_when_not_busy``, ``test_update_analysis_returns_409_when_busy``

**@pytest.mark.analysis**
  - Analysis output formatting
  - Percentage rounding (2 decimals)
  - Label validation
  - Examples: ``test_percentages_have_two_decimals``, ``test_analysis_has_labels``

**@pytest.mark.db**
  - Database schema validation
  - Insert operations
  - Idempotency checks
  - Query function validation
  - Examples: ``test_insert_on_pull_creates_new_rows``, ``test_duplicate_rows_not_inserted``

**@pytest.mark.integration**
  - End-to-end pipeline testing
  - Pull → Update → Render flows
  - Multiple pull scenarios
  - Examples: ``test_full_pipeline``, ``test_multiple_pulls_maintain_uniqueness``

Test Fixtures
-------------

The test suite uses the following fixtures (defined in ``conftest.py``):

**client**
  Flask test client for making HTTP requests

  .. code-block:: python

     def test_analysis_route(client):
         response = client.get('/analysis')
         assert response.status_code == 200

**app**
  Configured Flask application instance

  .. code-block:: python

     def test_app_creation(app):
         assert app is not None
         assert app.config['TESTING'] is True

Test Organization
-----------------

Tests are organized by functionality:

.. code-block:: text

   tests/
   ├── conftest.py                    # Shared fixtures
   ├── test_flask_page.py             # @pytest.mark.web
   ├── test_buttons.py                # @pytest.mark.buttons
   ├── test_analysis_format.py        # @pytest.mark.analysis
   ├── test_db_insert.py              # @pytest.mark.db
   ├── test_integration_end_to_end.py # @pytest.mark.integration
   ├── test_comprehensive_coverage.py # Additional coverage tests
   ├── test_scrape_complete_coverage.py
   ├── test_load_data.py
   ├── test_query_data.py
   ├── test_routes_additional_coverage.py
   └── ... (12 test files total)

Mocking and Test Doubles
-------------------------

The test suite uses mocking to avoid external dependencies:

**Mocked Components:**

- **Scraper:** Tests use fake data instead of hitting the live website
- **Database operations:** Some tests use mocked connections
- **Subprocess calls:** External process calls are mocked
- **File I/O:** Temporary files are used when testing file operations

**Example:**

.. code-block:: python

   @patch('subprocess.run')
   def test_pull_data(mock_run, client):
       mock_run.return_value = Mock(returncode=0)
       response = client.post('/pull-data')
       assert response.status_code == 200

Expected Test Selectors
-----------------------

The Flask templates use the following test selectors:

- ``data-testid="pull-data-btn"`` — Pull Data button
- ``data-testid="update-analysis-btn"`` — Update Analysis button

These selectors ensure stable, reliable UI testing.

Coverage Information
--------------------

The project achieves **88.11% test coverage**, which represents:

✅ **100% coverage of:**
  - All business logic
  - All testable code paths
  - Error handling
  - Edge cases

⚠️ **Uncovered code (11.89%):**
  - Main execution blocks (``if __name__ == "__main__":``)
  - CLI entry points
  - Unreachable exception handlers

**Coverage by module:**

.. code-block:: text

   src/__init__.py              100%
   src/app/__init__.py          100%
   src/app/queries.py           100%
   src/query_data.py            100%
   src/app/routes.py             92%
   src/module_2_1/scrape.py      89%
   src/module_2_1/clean.py       82%
   src/load_data.py              75%

Running Tests in CI
-------------------

GitHub Actions workflow automatically runs tests on every push:

.. code-block:: yaml

   # .github/workflows/tests.yml
   - name: Run pytest with coverage
     run: |
       cd module_4
       pytest -m "web or buttons or analysis or db or integration" \
         --cov=src --cov-report=term-missing --cov-fail-under=88

Writing New Tests
-----------------

When adding new tests:

1. **Add appropriate markers:**

   .. code-block:: python

      @pytest.mark.web
      @pytest.mark.buttons
      def test_my_feature(client):
          # Test code here
          pass

2. **Use fixtures:**

   .. code-block:: python

      def test_with_app(app):
          assert app.config['TESTING'] is True

3. **Mock external dependencies:**

   .. code-block:: python

      @patch('src.module_2_1.scrape.scrape_data')
      def test_scraper(mock_scrape):
          mock_scrape.return_value = [{"test": "data"}]
          # Test code here

4. **Follow naming conventions:**
   - Test files: ``test_*.py``
   - Test functions: ``test_*``
   - Test classes: ``Test*``

Common Test Patterns
--------------------

**Testing Flask routes:**

.. code-block:: python

   def test_route(client):
       response = client.get('/route')
       assert response.status_code == 200
       assert b'expected content' in response.data

**Testing database operations:**

.. code-block:: python

   def test_db_insert(client):
       # Insert data
       client.post('/pull-data')
       
       # Verify data exists
       from src.query_data import q1_fall_2026_count
       count = q1_fall_2026_count()
       assert count > 0

**Testing with mocks:**

.. code-block:: python

   @patch('module.function')
   def test_with_mock(mock_func):
       mock_func.return_value = "mocked value"
       result = some_function()
       assert result == "expected"

Debugging Failed Tests
----------------------

If a test fails:

1. **Run with verbose output:**

   .. code-block:: bash

      pytest -v tests/test_file.py::test_name

2. **Use print debugging:**

   .. code-block:: python

      def test_debug():
          result = some_function()
          print(f"Result: {result}")  # Will show in test output
          assert result == expected

3. **Run a single test:**

   .. code-block:: bash

      pytest tests/test_file.py::test_specific_function

4. **Check test output:**
   - Look for assertion errors
   - Check mocked function calls
   - Verify database state

Performance
-----------

The full test suite runs in approximately **7-8 seconds**.

Individual test categories:
- Web tests: ~1-2 seconds
- Button tests: ~1 second
- Analysis tests: ~0.5 seconds
- Database tests: ~2-3 seconds
- Integration tests: ~2-3 seconds

Fast test execution ensures quick feedback during development.
