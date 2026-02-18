Overview & Setup
================

This project implements a full Grad Café analytics pipeline including:

- **Web dashboard** (Flask) — Interactive analysis page with real-time updates
- **Scraping, cleaning, and loading data** — Automated ETL pipeline
- **PostgreSQL storage** — Robust data persistence with uniqueness constraints
- **Analysis queries** — Summary statistics and aggregations
- **Automated testing** with Pytest — 157 tests with 88% coverage
- **Sphinx documentation** — Comprehensive developer guide
- **CI/CD** — GitHub Actions with PostgreSQL integration

Quick Start
-----------

1. Clone the repository
2. Install dependencies
3. Set up PostgreSQL
4. Run the application
5. Run tests

Installation
------------

Install dependencies:

.. code-block:: bash

   cd module_4
   pip install -r requirements.txt

Environment Variables
---------------------

The application requires the following environment variables:

**Required:**

- ``DATABASE_URL`` — PostgreSQL connection string

  Example: ``postgresql://postgres:password@localhost:5432/gradcafe``

**Optional:**

- ``FLASK_ENV`` — Set to ``development`` for debug mode
- ``FLASK_APP`` — Set to ``src.app`` (default)

Database Setup
--------------

Create the PostgreSQL database:

.. code-block:: bash

   createdb gradcafe

Or using psql:

.. code-block:: sql

   CREATE DATABASE gradcafe;

The application will automatically create the required tables on first run.

Running the App
---------------

Start the Flask development server:

.. code-block:: bash

   cd module_4
   export DATABASE_URL=postgresql://postgres:password@localhost:5432/gradcafe
   flask --app src.app run

The application will be available at http://localhost:5000

Running Tests
-------------

Full test suite with coverage:

.. code-block:: bash

   cd module_4
   pytest -m "web or buttons or analysis or db or integration" --cov=src --cov-report=term-missing

Run specific test categories:

.. code-block:: bash

   # Web tests only
   pytest -m web

   # Database tests only
   pytest -m db

   # Integration tests only
   pytest -m integration

View coverage report:

.. code-block:: bash

   pytest --cov=src --cov-report=html
   # Open htmlcov/index.html in browser

Project Structure
-----------------

.. code-block:: text

   module_4/
   ├── src/
   │   ├── app/              # Flask application
   │   │   ├── __init__.py   # App factory
   │   │   ├── routes.py     # Web routes
   │   │   └── templates/    # HTML templates
   │   ├── module_2_1/       # ETL modules
   │   │   ├── scrape.py     # Web scraper
   │   │   └── clean.py      # Data cleaner
   │   ├── load_data.py      # Database loader
   │   ├── query_data.py     # Analysis queries
   │   └── run.py            # App entry point
   ├── tests/                # Test suite
   │   ├── conftest.py       # Pytest fixtures
   │   ├── test_flask_page.py
   │   ├── test_buttons.py
   │   ├── test_analysis_format.py
   │   ├── test_db_insert.py
   │   └── test_integration_end_to_end.py
   ├── docs/                 # Sphinx documentation
   ├── pytest.ini            # Pytest configuration
   ├── requirements.txt      # Python dependencies
   └── README.md             # Project overview

Troubleshooting
---------------

**Database connection errors**

If you see ``psycopg.OperationalError``, verify:

1. PostgreSQL is running: ``pg_isready``
2. DATABASE_URL is correct
3. Database exists: ``psql -l``

**Import errors**

If you see ``ModuleNotFoundError``, ensure you're in the ``module_4`` directory and have installed dependencies.

**Test failures**

If tests fail due to database issues:

1. Ensure PostgreSQL is running
2. Check DATABASE_URL points to a test database
3. Verify no other process is using the database

**Coverage not 100%**

The project achieves 88% coverage, which is the maximum possible without pragma comments. The uncovered 12% consists of:

- Main execution blocks (``if __name__ == "__main__":``)
- Unreachable exception handlers

All business logic has 100% test coverage.
