# jhu_software_concepts
Modern Software Concepts JHU class EN.605.256 (82) - Spring 2026

Grad School Café — Data Pipeline & Analysis Dashboard
Modern Concepts in Python — Spring 2026
Module 2 & Module 3 — Full Pipeline Implementation
Author: Eric Rying
Overview
This project implements a complete data engineering and analysis pipeline for graduate‑school admissions data sourced 
from TheGradCafe. The system spans:

Module 2: Web scraping, cleaning, and LLM‑based standardization

Module 3: PostgreSQL loading and a Flask‑based interactive analysis dashboard

The final deliverable is a polished, Bootstrap‑styled dashboard that computes:

Applicant counts

Acceptance rates

GPA/GRE averages

Fall 2026 metrics

University‑level summaries

Degree‑level acceptance rates

Custom queries (e.g., JHU CS Masters applicants, top CS PhD acceptances)

The pipeline is designed to be:

Reproducible — deterministic flow from raw HTML → cleaned JSON → PostgreSQL → dashboard

Robust — caching, error handling, normalization, and LLM standardization

Efficient — persistent HTTP connections, detail‑page caching, optimized parsing

Extensible — modular code structure for future assignments

Pipeline Diagram
Code
┌──────────────────┐
│   scrape.py       │
│  (Module 2)       │
│  • Fetch list pages
│  • Fetch detail pages
│  • Extract GPA/GRE/Term
│  • Cache detail pages
└─────────┬────────┘
          │ raw_applicant_data.json
          ▼
┌──────────────────┐
│    clean.py       │
│   (Module 2)      │
│  • Normalize fields
│  • Clean text/HTML
│  • Convert numeric fields
│  • LLM standardization
└─────────┬────────┘
          │ llm_extend_applicant_data.json
          ▼
┌──────────────────┐
│   load_data.py    │
│   (Module 3)      │
│  • Create table
│  • Normalize keys
│  • Insert into PostgreSQL
└─────────┬────────┘
          │ applicants table
          ▼
┌──────────────────┐
│     Flask App     │
│     run.py        │
│  • SQL queries
│  • Dashboard UI
│  • Update Analysis
└──────────────────┘
Module 2 — Web Scraping
scrape.py
This script collects raw admissions entries from TheGradCafe.

Key Features
Respects robots.txt

Uses a persistent urllib opener for efficiency

Extracts:

Program name

University

Status + status date

Degree level

Entry URL

Comments

Term (e.g., Fall 2026)

Citizenship

GPA, GRE total, GRE Verbal, GRE AW

Scans full page text for GRE/GPA (robust to HTML structure changes)

Uses a disk‑based shelve cache to avoid re-fetching detail pages

Saves output to:

Code
module_2/raw_applicant_data.json
Module 2 — Cleaning & LLM Standardization
clean.py
1. Basic Cleaning
Normalizes status labels

Strips HTML from comments

Converts empty strings to None

Converts GPA/GRE fields to numeric types

Normalizes citizenship to:

American

International

Other

Produces:

Code
cleaned_data.json
2. LLM Standardization
Uses the provided TinyLlama model to generate:

llm-generated-program

llm-generated-university

Final output:

Code
llm_extend_applicant_data.json
Module 3 — Database Loading
load_data.py
Loads the cleaned dataset into PostgreSQL.

Key Features
Computes the correct path to the JSON file

Creates the applicants table if needed

Normalizes JSON keys to database column names

Inserts rows with:

Code
ON CONFLICT (url) DO NOTHING
Prints number of inserted rows

This file forms the bridge between Module 2 and the Module 3 dashboard.

Module 3 — Flask Dashboard
run.py
Starts the Flask web server.

routes.py
Defines:

/ — main dashboard

/update-analysis — recompute statistics

queries.py
Executes SQL queries for:

Applicant counts

Acceptance rates

GPA/GRE averages

Fall 2026 metrics

University‑level summaries

Degree‑level acceptance rates

The dashboard displays results in a clean, Bootstrap‑styled interface with:

Loading spinner

Flash messages

Timestamp of last analysis

Summary tables

Running the Full Pipeline
1. Scrape
Code
python module_2/scrape.py
2. Clean
Code
python module_2/clean.py
3. Load into PostgreSQL
Code
python module_3/load_data.py
4. Start Dashboard
Code
python run.py
Then open:

Code
http://127.0.0.1
Project Structure
Code
jhu_software_concepts/
│
├── module_2/
│   ├── scrape.py
│   ├── clean.py
│   ├── raw_applicant_data.json
│   ├── cleaned_data.json
│   └── llm_extend_applicant_data.json
│
├── module_3/
│   ├── load_data.py
│   ├── queries.py
│   ├── routes.py
│   └── templates/
│       └── index.html
│
├── run.py
└── README.md
Requirements
Code
beautifulsoup4
Flask
psycopg2-binary
Notes for Graders
The scraper uses a polite delay and respects robots.txt..

Detail pages are cached to minimize load on TheGradCafe.

GPA/GRE extraction uses full‑page text scanning for robustness.

The pipeline is fully deterministic and reproducible.

The dashboard includes a diagnostic panel showing data completeness.

I can run using: powershell -ExecutionPolicy Bypass -File run.ps1
