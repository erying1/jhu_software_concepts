Overview
========

This project implements the Module 4 Flask application for the *Modern Concepts in Python* course.
It provides a complete data pipeline and dashboard for analyzing graduate‑school applicant data.

The system integrates:

- A Flask web application
- A PostgreSQL-backed data store
- A scraping and cleaning pipeline (Module 3)
- A fully tested route layer with busy‑state management
- A Sphinx documentation suite with autodoc support

Features
--------

- Dashboard displaying GPA, acceptance rates, and program statistics
- Buttons to trigger data pulls and refresh analysis
- JSON API responses for automated testing
- Graceful handling of scraper failures and malformed data
- 100% test coverage across all modules

Directory Structure
-------------------

::

    module_4/
        src/
            app/
                routes.py
                queries.py
            load_data.py
            query_data.py
        docs/
            conf.py
            index.rst
            overview.rst
            architecture.rst
            api_reference.rst
            testing_guide.rst
