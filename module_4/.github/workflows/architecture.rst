Architecture
============

The system consists of three main layers:

Web Layer (Flask)
-----------------
- Serves the analysis dashboard
- Handles pull-data and update-analysis actions
- Renders results and diagnostics

ETL Layer
---------
- ``scrape.py``: fetches Grad Café entries
- ``clean.py``: normalizes fields, merges LLM output
- ``load_data.py``: inserts rows into PostgreSQL

Database Layer
--------------
- Stores applicant records
- Enforces uniqueness constraints
- Supports analysis queries

Analysis Layer
--------------
- ``query_data.py`` computes summary statistics
- Results are displayed on the dashboard
