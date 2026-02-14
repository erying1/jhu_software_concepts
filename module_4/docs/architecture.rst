Architecture
============

This document describes the architecture of the Module 4 Flask application.

High-Level Components
---------------------

The system consists of four major layers:

1. **Web Layer (Flask)**
   - Defines routes for the dashboard, data pull, analysis refresh, and status checks.
   - Implements busy‑state protection to prevent concurrent pulls.
   - Renders Jinja2 templates with helper functions (fmt, pct, na).

2. **ETL Layer (Module 3 Integration)**
   - Scraper: Downloads applicant data from external sources.
   - Cleaner: Normalizes fields such as GPA, GRE, citizenship, and status.
   - Loader: Inserts cleaned data into PostgreSQL with idempotent inserts.

3. **Database Layer**
   - PostgreSQL database with a single `applicants` table.
   - Query functions compute averages, percentages, and counts.

4. **Testing Layer**
   - Pytest suite with 70+ tests.
   - Full mocking of subprocess, database, and file I/O.
   - Coverage enforcement at 100%.

Data Flow
---------

::

    scrape.py → clean.py → load_data.py → PostgreSQL → Flask dashboard

Busy-State Logic
----------------

The `pull_running` flag prevents overlapping pulls:

::

    if pull_running:
        return 409 or redirect

This ensures database consistency and predictable UI behavior.
