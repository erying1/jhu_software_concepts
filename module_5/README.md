# Grad Café Analytics — Module 5

A complete, secure, reproducible, and fully-tested data pipeline and Flask web application.

## Overview

Module 5 extends the earlier ETL + Flask system into a production-style application with:

- A full scrape → clean → load → analyze pipeline
- A Flask dashboard with "Pull Data" and "Update Analysis" actions
- Secure database access using environment variables
- A least-privilege PostgreSQL user
- A complete dependency graph
- A Snyk security scan (0 vulnerabilities)
- A clean `requirements.txt` and `setup.py`
- Fresh install instructions using both pip and uv
- Pylint-verified code quality

All components are fully tested using pytest, including integration tests and edge-case handling.

## Project Structure

```
module_5/
│
├── src/
│   ├── app/               # Flask app, routes, templates
│   ├── module_2_1/        # Scraper and cleaner
│   ├── load_data.py       # SQL-safe DB loader
│   ├── query_data.py      # Analysis queries
│   └── run.py             # Application entry point
│
├── tests/                 # Full pytest suite
├── dependency.svg         # Pydeps dependency graph
├── snyk-analysis.png      # Screenshot of Snyk CLI results
├── requirements.txt
├── setup.py
├── .env.example
└── README.md
```

## Fresh Install Instructions

Two supported methods: pip and uv.

### Option A — Using pip

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

### Option B — Using uv (fast, reproducible)

```bash
uv venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

uv pip sync requirements.txt
pip install -e .
```

> `pip install -e .` installs the project in editable mode so that imports like
> `from src.app import create_app` work consistently in local runs and CI.

---

## Database Security (Step 3)

### Environment Variables (No Hard-Coded Secrets)

The application reads all DB credentials from environment variables:

```
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

A `.env.example` file is included with placeholder values.
`.env` is listed in `.gitignore` to prevent committing real secrets.

### Least-Privilege PostgreSQL User

A dedicated DB user was created with only the permissions the app needs.

**SQL used (included in PDF submission):**

```sql
CREATE USER gradcafe_app WITH PASSWORD 'your_strong_password';

ALTER USER gradcafe_app NOSUPERUSER NOCREATEDB NOCREATEROLE;

GRANT CONNECT ON DATABASE "studentCourses" TO gradcafe_app;
GRANT USAGE ON SCHEMA public TO gradcafe_app;

GRANT SELECT, INSERT ON TABLE applicants TO gradcafe_app;
GRANT USAGE ON SEQUENCE applicants_p_id_seq TO gradcafe_app;
```

**Why these permissions?**

- `SELECT` — required for all analysis queries
- `INSERT` — required for loading scraped data
- No `DROP`/`ALTER`/`DELETE` — prevents destructive operations
- No superuser privileges — follows least-privilege best practices

---

## Running the Application

### 1. Activate your environment

```bash
.venv\Scripts\activate
```

### 2. Set environment variables

```bash
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=studentCourses
set DB_USER=gradcafe_app
set DB_PASSWORD=yourpassword
```

### 3. Start the Flask app

```bash
python -m src.run
```

---

## Running Tests

**Full suite:**

```bash
pytest -m "web or buttons or analysis or db or integration"
```

**Individual groups:**

```bash
pytest -m web
pytest -m db
pytest -m integration
```

---

## Code Quality (Pylint)

Pylint was used to ensure consistent style and maintainability.

**Command:**
```bash
pylint src --fail-under=10
```

**Result:** ✅ **10.00/10** — No errors or warnings

- `pylint` is included in `requirements.txt`
- Only `src/` is linted (not tests)
- Run after activating the virtual environment
- Project installed in editable mode (`pip install -e .`)

---

## Dependency Graph (Step 4)

Generated using:

```bash
pydeps src/run.py --noshow -T svg -o dependency.svg
```

### Key Dependencies Explained

The dependency graph visualizes the module structure of the Grad School Café application, with `run.py` serving as the main entry point that initializes the Flask application. The `src.app` module contains the Flask application factory and route handlers (`src.app.routes`), which orchestrate HTTP requests and responses for the web interface. The `src.app.routes` module depends on `src.query_data` for database analysis queries and `src.load_data` for database connections, demonstrating clear separation between the web layer and data access layer. The data pipeline modules (`src.module_2_1.scrape`, `src.module_2_1.clean`, and `src.load_data`) handle the scraping, cleaning, and loading workflow but remain independent of the Flask web layer. The `src.query_data` module provides SQL query functions with safe parameter binding and LIMIT enforcement, serving as the primary interface between Flask routes and the PostgreSQL database. Notably, the graph shows no circular dependencies, confirming a clean, unidirectional dependency structure that promotes maintainability and testability. All external dependencies like Flask, psycopg2, and BeautifulSoup are isolated to their respective modules, preventing tight coupling across the application.

The file `dependency.svg` is included in the repository.

---

## Security Scan (Snyk)

### CLI Scan

```bash
snyk test
```

**Results:**
- 59 dependencies tested
- 0 vulnerabilities found

Screenshot: `snyk-analysis.png`

### Static Code Analysis (Snyk Code)

- 77 issues (1 high, 63 medium, 13 low)
- These are code-quality warnings, not dependency vulnerabilities
- Remediation is not required for Module 5

---

## Packaging (setup.py)

A `setup.py` file is included to make the project installable:

- Ensures consistent imports regardless of working directory
- Supports `pip install -e .`
- Enables reproducible environments

---

## Requirements File (requirements.txt)

Includes:

- Runtime dependencies (Flask, psycopg2-binary, beautifulsoup4, requests, werkzeug)
- Testing tools (pytest, pytest-cov)
- Code quality tools (pylint, pydeps)
- Documentation tools (sphinx, sphinx-rtd-theme, sphinx-autobuild)

This ensures a fresh environment can run the project from scratch.

---

## License

This project is part of the JHU "Modern Software Development in Python" course (Spring 2026).
For educational use only.

