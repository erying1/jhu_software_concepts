# jhu_software_concepts
Modern Software Concepts JHU class EN.605.256 (82) - Spring 2026

==============================================================
Modern Concepts in Python: Spring 2026
Module 3 Assignment: Database Queries & Analysis Dashboard
Author: Eric Rying
==============================================================

**Overview**
Module 3 extends the Grad School Café data pipeline by adding a full PostgreSQL‑backed analysis dashboard built with Flask.
This module demonstrates:

SQL query design

Database integration using psycopg

A dynamic Flask web interface

A data‑pull workflow (scrape → clean → load → analyze)

A polished Bootstrap UI with spinners, flash messages, and timestamps

The result is a fully functional, assignment‑ready analytics page that summarizes key trends from Grad Café applicant data.

Repository Structure
module_3/
    README.md                ← this file
app/
    __init__.py             ← Flask app factory + Jinja filters
    routes.py               ← routes for analysis + data pull
    queries.py              ← wrapper for SQL query functions
    templates/
        analysis.html       ← Bootstrap dashboard UI
query_data.py               ← raw SQL queries (Q1–Q11)
load_data.py                ← loads cleaned JSON into PostgreSQL


**How the System Works**
**1. Scrape Data (Module 2)**
Triggered via the dashboard’s Pull Data button:

Runs scrape.py to collect Grad Café entries

Runs clean.py to normalize fields

Produces cleaned_applicant_data.json

**2. Load Data into PostgreSQL**
load_data.py inserts cleaned records into the applicants table.

**3. Run SQL Queries (Module 3)**
query_data.py defines 11 queries, including:

Fall 2026 applicant counts

International percentage

GPA/GRE averages

Acceptance rates

JHU CS Masters applicants

Top‑school CS PhD acceptances

Custom questions (GPA by nationality, degree distribution)

**4. Display Results in Flask Dashboard**
analysis.html renders:

A timestamped analysis summary

Bootstrap tables

Flash messages

A loading spinner overlay

Custom question tables

**Running the Dashboard**
1. Start PostgreSQL
Ensure your database is running and contains the applicants table.

2. Install dependencies
Code
pip install -r requirements.txt

4. Run the Flask app
Code
flask --app app run
Visit:

Code
http://127.0.0.1:5000/

**Key Features**
✔ Update Analysis
Re‑runs all SQL queries and refreshes the dashboard.

✔ Pull Data
Runs the full scrape → clean → load pipeline.

✔ Bootstrap UI Enhancements
Spinner overlay during long operations

Flash messages for user feedback

Clean, readable tables

Timestamp showing last analysis refresh

✔ Safe Query Handling
Queries gracefully handle missing or NULL values to avoid runtime errors.

**Known Limitations**
Grad Café list pages do not include GPA, GRE, or citizenship, so many averages return None.

Fall 2026 term data is sparse in scraped pages.

The dashboard currently displays tables only (charts optional).

