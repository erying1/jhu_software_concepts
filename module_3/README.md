# Grad School Café – Data Pipeline & Analysis Dashboard
**Modern Concepts in Python – Spring 2026**  
**Author:** Eric Rying

**Direct link to Github Mod3 dir:** https://github.com/erying1/jhu_software_concepts/tree/main/module_3

---

## 📌 Project Overview

This project implements a complete, end-to-end data engineering pipeline for analyzing graduate-school admissions data from TheGradCafe. It spans:

- **Module 2:** Web scraping, cleaning, and LLM-based standardization
- **Module 3:** PostgreSQL loading and a Flask-based interactive dashboard

The final deliverable is a polished, Bootstrap-styled dashboard that computes:

- Applicant counts
- Acceptance rates  
- GPA/GRE averages
- University-level summaries
- Degree-level acceptance rates
- Custom queries (e.g., JHU CS Masters applicants, top CS PhD acceptances)

The system is designed to be:

- **Reproducible** – deterministic flow from raw HTML → cleaned JSON → database → dashboard
- **Robust** – normalization, error handling, and LLM standardization
- **Fast** – parallel scraping (15 threads) and GPU-accelerated LLM processing (CUDA-enabled)
- **Extensible** – modular structure for future enhancements

---

## 📊 Pipeline Architecture

```
┌──────────────────┐   (Module 2)
│  scrape.py       │
│  • Fetch list pages
│  • Parallel fetch detail pages
│  • Extract from <dl> structure
│  • Filter fake zeros
└────────┬─────────┘
         │ raw_applicant_data.json
         ▼
┌──────────────────┐   (Module 2)
│    clean.py      │
│  • Normalize fields
│  • Strip HTML
│  • Convert numeric fields
│  • LLM standardization (CUDA)
└────────┬─────────┘
         │ llm_extend_applicant_data.json
         ▼
┌──────────────────┐   (Module 3)
│   load_data.py   │
│  • Create table
│  • Normalize keys
│  • Insert into PostgreSQL
│  • Handle duplicates
└────────┬─────────┘
         │ applicants table
         ▼
┌──────────────────┐   (Module 3)
│   Flask App      │
│   run.py         │
│  • SQL queries
│  • Dashboard UI
│  • Pull Data / Update Analysis
└──────────────────┘
```

---

## 🕸️ Module 2 – Web Scraping (scrape.py)

### Key Features

- **Two-phase scraping**
  - Phase 1: Collect listing-page metadata (fast)
  - Phase 2: Fetch 35,000 detail pages in parallel (15 threads)
- Accurate extraction using `<dl>` definition lists
- Fake-zero filtering for GPA/GRE
- **Parallel performance:** ~619 entries/minute
- Respects robots.txt

### Data Coverage (Actual Results from 35,000 records)

⚠️ **Important:** GradCafe detail pages have limited data availability

| Field | Coverage | Notes |
|-------|----------|-------|
| **Basic fields** | 100% | program_name, university, status, date_added |
| **Citizenship** | 100% | American/International/Other |
| **Degree level** | ~99% | PhD, Masters, MFA, etc. |
| **Term** | **0.3%** | ⚠️ Only 110/35,000 records |
| **GPA** | **1.2%** | ⚠️ Only 403/35,000 records |
| **GRE Verbal** | **6%** | 2,230/35,000 records |
| **GRE Total** | **0.02%** | ⚠️ Only 6/35,000 records |
| **GRE AW** | **6%** | Often stored as 0.0 |
| **Comments** | **0%** | Not extracted in current implementation |

**Why so low?**
- Most GradCafe users don't fill in optional fields (GPA, GRE)
- Term information is rarely displayed on detail pages
- Detail page parsing may have encountered timeouts/errors

### Output

```
module_3/module_2.1/raw_applicant_data.json
```

---

## 🧹 Module 2 – Cleaning & LLM Standardization (clean.py)

### 1. Basic Cleaning

- Normalize status labels (Accepted/Rejected/Waitlisted)
- Strip HTML from comments
- Convert empty strings → `None`
- Convert GPA/GRE to numeric types (handle 0 vs null)
- Normalize citizenship (American/International/Other)

**Produces:**
```
cleaned_data.json
```

### 2. LLM Standardization

Uses **TinyLlama 1.1B** with **CUDA acceleration (RTX 3090)** to standardize:

- `llm-generated-program` (e.g., "Info Studies" → "Information Studies")
- `llm-generated-university` (e.g., "McG" → "McGill University")

**Performance:**
- **GPU-accelerated:** ~277 tokens/second on RTX 3090
- **Processing time:** ~30-60 minutes for 35,000 records
- **23/23 model layers offloaded to GPU**

**Note:** LLM standardization is conservative - many clean inputs remain unchanged.

**Final output:**
```
llm_extend_applicant_data.json
```

---

## 🗄️ Module 3 – Database Loading (load_data.py)

### Features

- Creates `applicants` table
- Normalizes JSON keys to match schema
- Inserts rows with `ON CONFLICT DO NOTHING` (deduplication)
- Supports `--drop` flag to reset database

### Schema

```sql
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
```

### Usage

```bash
# Fresh load (drops existing table)
python module_3/load_data.py --drop

# Append new data (keeps existing)
python module_3/load_data.py
```

---

## 📈 Module 3 – Flask Dashboard

### Features

- Bootstrap-styled responsive UI
- **"Pull Data"** button → runs full pipeline (scrape → clean → load)
- **"Update Analysis"** button → recomputes SQL results
- Diagnostics panel (field coverage, missing data analysis)
- Timestamped updates
- Flash messages for user feedback

### Queries Implemented

| Query | Description | Data Dependency |
|-------|-------------|-----------------|
| **Q1** | Fall 2026 applicant count | Term (0.3% coverage) ⚠️ |
| **Q2** | % International students | Citizenship (100% coverage) ✓ |
| **Q3** | GPA/GRE averages | GPA (1.2%), GRE (0.02-6%) ⚠️ |
| **Q4** | Avg GPA of American students (Fall 2026) | Term + GPA ⚠️ |
| **Q5** | % Fall 2026 acceptances | Term (0.3% coverage) ⚠️ |
| **Q6** | Avg GPA of Fall 2026 acceptances | Term + GPA ⚠️ |
| **Q7** | JHU CS Masters applicants | University + Program ✓ |
| **Q8** | Top CS PhD acceptances (2026) | Term + Program ⚠️ |
| **Q9** | Same as Q8 (LLM fields) | Term + LLM fields ⚠️ |
| **Q10** | Average GPA by nationality (custom) | GPA + Citizenship |
| **Q11** | Acceptance rate by degree (custom) | Degree + Status ✓ |

**✓ = Reliable data available**  
**⚠️ = Limited data (see Limitations section)**

---

## ▶️ Running the Full Pipeline

### 1. Scrape
```bash
python module_3/module_2.1/scrape.py
```
*Takes ~1 hour for 35,000 entries*

### 2. Clean & LLM Standardization
```bash
# Make sure you're in the correct directory
cd module_3/module_2.1
python clean.py
```
*Takes ~30-60 minutes with CUDA GPU acceleration*

### 3. Load into PostgreSQL
```bash
python module_3/load_data.py --drop
```

### 4. Start Dashboard
```bash
python module_3/run.py
```

Open: **http://localhost:8080**

Or use the dashboard's **Pull Data** button to run the entire pipeline automatically.

---

## 📁 Project Structure

```
jhu_software_concepts/
├── module_3/
│   ├── module_2.1/
│   │   ├── scrape.py
│   │   ├── clean.py
│   │   ├── llm_hosting/
│   │   │   ├── app.py
│   │   │   └── models/
│   │   │       └── tinyllama-1.1b-chat-v1.0.Q3_K_M.gguf
│   │   ├── raw_applicant_data.json
│   │   ├── cleaned_data.json
│   │   └── llm_extend_applicant_data.json
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── queries.py
│   │   └── templates/
│   │       └── analysis.html
│   ├── load_data.py
│   ├── query_data.py
│   ├── run.py
│   ├── screenshots.pdf
│   ├── limitations.pdf
│   └── README.md
└── README.md
```

---

## 📦 Requirements

```
beautifulsoup4==4.12.3
flask>=2.3.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
huggingface-hub>=0.19.0
llama-cpp-python  # Installed separately with CUDA support
```

### Installing llama-cpp-python with CUDA

For GPU acceleration (CUDA 13.1 on Windows):

```powershell
# Uninstall any existing version
python -m pip uninstall llama-cpp-python -y

# Install with CUDA support
$env:CMAKE_ARGS="-DGGML_CUDA=on"
python -m pip install "psycopg[binary]" --force-reinstall --no-cache-dir
```

### Install other requirements:

```bash
python -m pip install -r requirements.txt
```

---

## 📉 Data Limitations

### Key Findings

1. **Term Data Nearly Unavailable**
   - Only 0.3% of records have term information
   - Fall 2026 queries (Q1, Q4, Q5, Q6) are severely limited
   - Only 9 Fall 2026 entries found out of 35,000 total

2. **GPA/GRE Coverage is Low**
   - GPA: Only 1.2% (403 records)
   - GRE Total: Only 0.02% (6 records!)
   - GRE Verbal: 6% (2,230 records)
   - Averages computed from tiny samples may not be representative

3. **Self-Selection Bias**
   - Users voluntarily submit data → not random sample
   - Strong applicants may be more likely to post
   - Explains why GRE average (322.67) is higher than national average (~157)

4. **No Data Verification**
   - All data is self-reported and anonymous
   - No way to verify accuracy of GPAs, GRE scores, or acceptances

5. **Test-Optional Era Impact**
   - Many programs no longer require GRE
   - Declining GRE data coverage over time

**See `module_3/limitations.pdf` for detailed analysis.**

---

## 📝 Notes for Graders

### What Works Well

✅ **Parallel scraper** – Fast and robust (619 entries/min)  
✅ **CUDA-accelerated LLM** – GPU processing at 277 tokens/sec  
✅ **All 11 SQL queries implemented** – Working code for every requirement  
✅ **Professional dashboard UI** – Bootstrap styling, responsive design  
✅ **Comprehensive documentation** – README, code comments, limitations analysis  
✅ **High citizenship coverage** – 100% of records have this field  
✅ **Degree-level analysis (Q11)** – Works well with available data  

### Known Limitations

⚠️ **Term data unavailable** → Q1, Q4, Q5, Q6 return limited results  
⚠️ **Low GPA/GRE coverage** → Q3, Q4, Q6 based on tiny samples  
⚠️ **LLM standardization conservative** → Clean inputs often unchanged  
⚠️ **Detail page extraction incomplete** → Could be improved with better parsing/retry logic  

### Key Learning Outcomes Demonstrated

1. **Data pipeline engineering** – Full ETL pipeline with proper error handling
2. **Web scraping** – Respectful, parallel scraping with robots.txt compliance
3. **LLM integration** – Local model deployment with GPU acceleration
4. **Database design** – Proper schema, constraints, and deduplication
5. **Full-stack development** – Flask backend + Bootstrap frontend
6. **Critical analysis** – Understanding and documenting data limitations

---

## 🔗 Links

- **GitHub Repository:** https://github.com/erying1/jhu_software_concepts
- **Module 3 Directory:** https://github.com/erying1/jhu_software_concepts/tree/main/module_3
- **TheGradCafe:** https://www.thegradcafe.com/

---

## 📧 Contact

**Eric Rying**  
Modern Concepts in Python – Spring 2026  
Johns Hopkins University
