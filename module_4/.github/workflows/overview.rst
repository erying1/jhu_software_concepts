Overview & Setup
================

This project implements a full Grad Café analytics pipeline including:

- Web dashboard (Flask)
- Scraping, cleaning, and loading data
- PostgreSQL storage
- Analysis queries
- Automated testing with Pytest
- Sphinx documentation

Setup
-----

Install dependencies:

.. code-block:: bash

   pip install -r requirements.txt

Environment Variables
---------------------

The application requires:

- ``DATABASE_URL`` — PostgreSQL connection string

Running the App
---------------

.. code-block:: bash

   flask --app src.app run

Running Tests
-------------

.. code-block:: bash

   pytest -q --cov=src
