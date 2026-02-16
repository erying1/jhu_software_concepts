Architecture
============

This document describes the architecture of the Grad Café Analytics system.

High-Level Components
---------------------

The system consists of three core layers plus a testing layer:

1. **Web Layer (Flask)**

   - ``src/app/routes.py`` — Defines routes for the dashboard (``/analysis``),
     data pull (``/pull-data``), analysis refresh (``/update-analysis``), and
     status checks (``/status``).
   - ``src/app/__init__.py`` — App factory (``create_app``) that registers the
     blueprint and Jinja2 template filters.
   - ``src/app/pages.py`` — HTML rendering helpers for the analysis template.
   - ``src/app/queries.py`` — Thin wrapper that calls ``query_data`` functions
     and computes scraper diagnostics for the dashboard.
   - Implements busy-state protection via a ``pull_running`` flag to prevent
     concurrent data pulls.

2. **ETL Layer (Scrape → Clean → Load)**

   - ``src/module_2_1/scrape.py`` — Scrapes GradCafe listing and detail pages
     in parallel, respecting ``robots.txt``. Outputs raw JSON.
   - ``src/module_2_1/clean.py`` — Normalizes status labels, strips HTML,
     converts numeric fields, and batch-processes program/university names
     through a local LLM for standardization.
   - ``src/load_data.py`` — Reads the cleaned JSON and inserts records into
     PostgreSQL. Uses ``ON CONFLICT (url) DO NOTHING`` for idempotent inserts.

3. **Database Layer (PostgreSQL)**

   - Single ``applicants`` table with 16 columns including GPA, GRE scores,
     status, citizenship, and LLM-generated standardized fields.
   - ``src/query_data.py`` — Contains 11 analysis functions (``q1`` through
     ``q11``) that compute counts, averages, and percentages via SQL.
   - ``get_all_analysis()`` aggregates all query results into a single
     dictionary consumed by the Flask routes.

4. **Testing Layer**

   - 180+ tests organized by marker: ``web``, ``buttons``, ``analysis``,
     ``db``, ``integration``.
   - Full mocking of subprocess calls, database connections, and file I/O.
   - 100% statement coverage enforced by ``pytest-cov``.

Data Flow
---------

::

    scrape.py → clean.py → load_data.py → PostgreSQL
                                              ↓
                                    query_data.py → routes.py → analysis.html

Busy-State Logic
----------------

The ``pull_running`` global flag prevents overlapping data pulls::

    POST /pull-data
        if pull_running → 409 (busy)
        else → set pull_running = True
             → run scrape → clean → load
             → set pull_running = False

While ``pull_running`` is True, both ``/pull-data`` and ``/update-analysis``
return 409 to protect database consistency.

Uniqueness Policy
-----------------

Each applicant record has a unique ``url`` field (the GradCafe entry URL).
The database enforces ``UNIQUE(url)`` and inserts use
``ON CONFLICT (url) DO NOTHING``, so duplicate pulls are safe and idempotent.
