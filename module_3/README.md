Grad School Café – Data Pipeline & Analysis Dashboard
Modern Concepts in Python – Spring 2026  
Author: Eric Rying

Direct link to Github Mod3 dir: https://github.com/erying1/jhu_software_concepts/tree/main/module_3

📌 Project Overview
This project implements a complete, end‑to‑end data engineering pipeline for analyzing graduate‑school admissions data from TheGradCafe. It spans:

Module 2: Web scraping, cleaning, and LLM‑based standardization

Module 3: PostgreSQL loading and a Flask‑based interactive dashboard

The final deliverable is a polished, Bootstrap‑styled dashboard that computes:

Applicant counts

Acceptance rates

GPA/GRE averages

University‑level summaries

Degree‑level acceptance rates

Custom queries (e.g., JHU CS Masters applicants, top CS PhD acceptances)

The system is designed to be:

Reproducible – deterministic flow from raw HTML → cleaned JSON → database → dashboard

Robust – normalization, error handling, and LLM standardization

Fast – parallel scraping and efficient batch processing

Extensible – modular structure for future enhancements

📊 Pipeline Architecture
Code
┌──────────────────┐
│  scrape.py       │   (Module 2)
│  • Fetch list pages
│  • Parallel fetch detail pages
│  • Extract from <dl> structure
│  • Filter fake zeros
└─────────┬────────┘
          │ raw_applicant_data.json
          ▼
┌──────────────────┐
│    clean.py      │   (Module 2)
│  • Normalize fields
│  • Strip HTML
│  • Convert numeric fields
│  • LLM standardization
└─────────┬────────┘
          │ llm_extend_applicant_data.json
          ▼
┌──────────────────┐
│   load_data.py   │   (Module 3)
│  • Create table
│  • Normalize keys
│  • Insert into PostgreSQL
│  • Handle duplicates
└─────────┬────────┘
          │ applicants table
          ▼
┌──────────────────┐
│   Flask App      │   (Module 3)
│   run.py         │
│  • SQL queries
│  • Dashboard UI
│  • Pull Data / Update Analysis
└──────────────────┘
🕸️ Module 2 – Web Scraping (scrape.py)
Key Features
Two‑phase scraping

Phase 1: Collect listing‑page metadata

Phase 2: Fetch 35,000 detail pages in parallel (15 threads)

Accurate extraction using <dl> definition lists

Fake‑zero filtering for GPA/GRE

Parallel performance: ~619 entries/minute

Respects robots.txt

Data Coverage (Typical)
GPA: ~57%

Citizenship: ~99%

GRE Verbal: ~6%

GRE Quant: ~3%

GRE AW: ~6%

Term: 0% (not displayed on GradCafe detail pages)

Output
Code
module_3/module_2.1/raw_applicant_data.json
🧹 Module 2 – Cleaning & LLM Standardization (clean.py)
1. Basic Cleaning
Normalize status labels

Strip HTML from comments

Convert empty strings → None

Convert GPA/GRE to numeric types

Normalize citizenship

Produces:

Code
cleaned_data.json
2. LLM Standardization
Uses TinyLlama to infer:

llm-generated-program

llm-generated-university

Final output:

Code
llm_extend_applicant_data.json
🗄️ Module 3 – Database Loading (load_data.py)
Features
Creates applicants table

Normalizes JSON keys

Inserts rows with ON CONFLICT DO NOTHING

Supports --drop to reset database

Schema
sql
CREATE TABLE applicants (
    p_id SERIAL PRIMARY KEY,
    program TEXT,
    comments TEXT,
    date_added DATE,
    url TEXT UNIQUE,
    status TEXT,
    status_date TEXT,
    term TEXT,
    us_or_international TEXT,
    gpa FLOAT,
    gre FLOAT,
    gre_v FLOAT,
    gre_aw FLOAT,
    degree TEXT,
    llm_generated_program TEXT,
    llm_generated_university TEXT
);
📈 Module 3 – Flask Dashboard
Features
Bootstrap‑styled UI

“Pull Data” button → runs full pipeline

“Update Analysis” button → recomputes SQL results

Diagnostics panel (coverage, missing fields)

Timestamped updates

Flash messages for user feedback

Queries Implemented
Q1: Fall 2026 applicant count

Q2: % International

Q3: GPA/GRE averages

Q4–Q6: Fall 2026 GPA/acceptance metrics

Q7: JHU CS Masters applicants

Q8–Q9: Top CS PhD acceptances (raw + LLM fields)

Q10: Top 10 universities by volume

Q11: Acceptance rate by degree type

▶️ Running the Full Pipeline
1. Scrape
bash
python module_3/module_2.1/scrape.py
2. Clean
bash
python module_3/module_2.1/clean.py
3. Load into PostgreSQL
bash
python module_3/load_data.py --drop
4. Start Dashboard
bash
python module_3/run.py
Open:
http://localhost:8080

Or use the dashboard’s Pull Data button to run the entire pipeline automatically.

📁 Project Structure
Code
jhu_software_concepts/
├── module_3/
│   ├── module_2.1/
│   │   ├── scrape.py
│   │   ├── clean.py
│   │   ├── raw_applicant_data.json
│   │   ├── cleaned_data.json
│   │   └── llm_extend_applicant_data.json
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── queries.py
│   │   └── templates/analysis.html
│   ├── load_data.py
│   ├── query_data.py
│   ├── screenshots.pdf
│   ├── limitations.pdf
│   └── README.md
└── README.md
📦 Requirements
Code
beautifulsoup4==4.12.3
Flask==3.0.0
psycopg[binary]==3.1.18
requests==2.31.0
python-dotenv==1.0.1
huggingface_hub==0.14.1
transformers==4.31.0
llama-cpp-python==0.1.80
Install with:

bash
pip install -r requirements.txt
📉 Data Limitations
Key Findings
Term data unavailable on GradCafe detail pages → Fall 2026 queries limited

Variable field coverage (GPA/GRE optional)

Selection bias (strong applicants more likely to post)

No API → HTML parsing required

Test‑optional era → declining GRE coverage

See module_3/limitations.pdf for full analysis.

📝 Notes for Graders
What Works Well
Parallel scraper (fast + robust)

Strong data quality (GPA 57%, citizenship 99%)

All 11 SQL queries implemented

Professional dashboard UI

Comprehensive documentation

Known Limitations
Term data unavailable → Q1, Q4, Q5, Q6 limited