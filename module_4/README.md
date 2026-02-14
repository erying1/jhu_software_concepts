📘 README.md — Grad Café Analytics (Module 4)
Overview
This project implements a fully tested, fully documented analytics pipeline for the Grad Café admissions results dataset.
It extends the Module 3 ETL + Flask system with:

A complete Pytest suite (web, buttons, analysis, DB, integration)

100% test coverage across all modules

Sphinx documentation published to Read the Docs

GitHub Actions CI with PostgreSQL

A clean, testable Flask application using a factory pattern

The system provides:

A web dashboard (/analysis)

“Pull Data” and “Update Analysis” actions

Scraping → cleaning → loading into PostgreSQL

Summary analysis queries rendered in the UI

Project Structure
Code
module_4/
│
├── src/
│   ├── app/                # Flask app, routes, templates
│   ├── module_2_1/         # Scrape + clean modules from M3
│   ├── load_data.py        # DB loader
│   ├── query_data.py       # Analysis queries
│   └── run.py              # App entry point
│
├── tests/                  # Full Pytest suite
│
├── docs/                   # Sphinx documentation
│
├── pytest.ini
├── requirements.txt
├── coverage_summary.txt
├── actions_success.png
└── .github/workflows/tests.yml
Running the Application
1. Install dependencies
bash
pip install -r requirements.txt
2. Set environment variables
The application uses:

Code
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<dbname>
Example for local development:

bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gradcafe
3. Run the Flask app
bash
flask --app src.app run
Running Tests
Full suite with coverage
bash
pytest -q --cov=src --cov-report=term-missing
Marker‑based execution (required by assignment)
bash
pytest -m "web or buttons or analysis or db or integration"
Markers Used
Marker	Purpose
web	Flask page rendering
buttons	Pull/update behavior + busy‑state logic
analysis	Formatting, labels, rounding
db	PostgreSQL schema, inserts, idempotency
integration	End‑to‑end pipeline tests
All tests in this project are marked as required.

GitHub Actions CI
A full CI pipeline is included under:

Code
module_4/.github/workflows/tests.yml
The workflow:

Starts PostgreSQL 15

Installs dependencies

Sets DATABASE_URL

Runs the full Pytest suite

Enforces 100% coverage

A screenshot of a successful run is included as:

Code
module_4/actions_success.png
Sphinx Documentation
Sphinx docs are located in:

Code
module_4/docs/
They include:

Overview & setup

Architecture (Web, ETL, DB)

API reference (autodoc)

Testing guide (markers, fixtures)

Build instructions

Build locally
bash
cd module_4/docs
make html
Published Documentation
(Insert your Read the Docs link here once published)

Key Features
✔ Testable Flask App
Uses a factory pattern and stable HTML selectors (data-testid="...") for reliable UI tests.

✔ Full ETL Pipeline
Scraping → cleaning → LLM‑enhanced normalization → PostgreSQL loading.

✔ Analysis Engine
Computes summary statistics used by the dashboard.

✔ 100% Test Coverage
All modules fully covered, including error paths and edge cases.

✔ CI + Documentation
Automated testing and published developer documentation.

Developer Notes
All external processes (scraper, cleaner, loader) are mocked in tests.

No test depends on live network calls.

Busy‑state logic is deterministic and observable.

Database tests use DATABASE_URL to allow CI overrides.

License
This project is part of the JHU “Modern Software Development in Python” course (Spring 2026).
For educational use only.