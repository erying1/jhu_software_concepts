Overview & Setup
================

This project implements the Module 4 Flask application for the *Modern Concepts in Python* course.
It provides a complete data pipeline and dashboard for analyzing graduate-school applicant data.

The system integrates:

- A Flask web application serving an analysis dashboard
- A PostgreSQL-backed data store with idempotent inserts
- A scraping and cleaning pipeline (ETL from Module 2/3)
- A fully tested route layer with busy-state management
- Sphinx documentation with autodoc for all key modules

Environment Variables
---------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Variable
     - Description
   * - ``DATABASE_URL``
     - PostgreSQL connection string (e.g. ``postgresql://postgres:pass@localhost:5432/studentCourses``). If not set, falls back to local defaults.
   * - ``PGPASSWORD``
     - Password for local PostgreSQL when ``DATABASE_URL`` is not set. Defaults to local dev password.

How to Run the App
------------------

1. Clone the repository and ``cd module_4``.
2. Create a virtual environment and install dependencies::

       python -m venv .venv
       .venv\Scripts\activate        # Windows
       source .venv/bin/activate     # macOS/Linux
       pip install -r requirements.txt

3. Ensure PostgreSQL is running and the ``studentCourses`` database exists.
4. Start the Flask development server::

       python -m src.run

5. Open http://localhost:5000/analysis in your browser.

How to Run Tests
----------------

Run the full marked test suite with coverage::

    pytest -m "web or buttons or analysis or db or integration" --cov=src --cov-report=term-missing --cov-fail-under=100

Run a single marker group::

    pytest -m db
    pytest -m web

Directory Structure
-------------------

::

    module_4/
        src/
            app/
                __init__.py        # Flask app factory (create_app)
                routes.py          # HTTP route handlers
                queries.py         # Query wrappers for dashboard
                pages.py           # HTML rendering helpers
            module_2_1/
                scrape.py          # GradCafe web scraper
                clean.py           # Data cleaning + LLM pipeline
            load_data.py           # JSON -> PostgreSQL loader
            query_data.py          # SQL analysis functions
            run.py                 # App entry point
        tests/                     # All test files
        docs/                      # Sphinx documentation source
        pytest.ini
        requirements.txt
        README.md
