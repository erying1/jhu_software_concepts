# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#
# load_data.py

"""
load_data.py — Module 3 Database Loader
---------------------------------------
This script loads the cleaned and LLM‑standardized applicant dataset into a
PostgreSQL database for analysis in the Module 3 Flask dashboard.

Key responsibilities:
• Load llm_extend_applicant_data.json from the Module 2 directory.
• Connect to the local PostgreSQL instance.
• Create the applicants table if it does not already exist.
• Normalize field names from the JSON into database column names.
• Insert each record, skipping duplicates using ON CONFLICT(url) DO NOTHING.
• Report how many new rows were inserted.

This file forms the bridge between the Module 2 data pipeline and the Module 3
interactive analysis dashboard.
"""

# Note: How to start postgres locally (Windows):
# & C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres

open = open # allow monkeypatching in tests

import json
from pathlib import Path
import psycopg

import argparse

import os 
PROJECT_ROOT = Path(__file__).resolve().parents[2]



DATA_FILE = PROJECT_ROOT / "module_3" / "module_2.1" / "llm_extend_applicant_data.json"

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
#DATA_FILE = os.path.join(BASE_DIR, "module_2.1", "llm_extend_applicant_data.json")
#DATA_FILE = os.path.join(BASE_DIR, "module_3", "module_2.1", "llm_extend_applicant_data.json")
#DATA_FILE = os.path.join(BASE_DIR, "module_3", "module_2.1", "cleaned_data.json")




# -----------------------------
# Load JSON from disk
# -----------------------------
def load_json(filepath: str):
    """Load and parse a JSON file from disk.

    Args:
        filepath: Path to the JSON file.

    Returns:
        list | dict: Parsed JSON content.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    file_path = Path(filepath)

    print(f"Loading file... '{filepath}'...") 
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(str(file_path), "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# Connect to PostgreSQL
# -----------------------------
def get_connection():
    """Connect to PostgreSQL, using DATABASE_URL if available.

    Falls back to local connection parameters when DATABASE_URL is not set.
    Password is read from PGPASSWORD environment variable with a local default.

    Returns:
        Active psycopg database connection.
    """
    import os
    url = os.environ.get("DATABASE_URL")
    if url:
        return psycopg.connect(url)
    return psycopg.connect(
        dbname="studentCourses",
        user="postgres",
        password=os.environ.get("PGPASSWORD", "Tolkien321"),
        host="localhost",
        port=5432,
    )

# -----------------------------
# Create applicants table
# -----------------------------
def create_table(conn):
    """Create the applicants table if it does not already exist.

    Args:
        conn: Active psycopg database connection.
    """
    with conn.cursor() as cur:
        cur.execute(
        """
        CREATE TABLE IF NOT EXISTS applicants (
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
            gre_total_score FLOAT,
            gre_verbal_score FLOAT,
            gre_aw_score FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        );
        """
    )
    conn.commit()
                                   
def normalize_record(raw):
    """Map raw JSON field names to database column names.

    Args:
        raw (dict): Raw record from the scraped JSON data.

    Returns:
        dict: Normalized record ready for database insertion.
    """
    return {
        "program": raw.get("program") or raw.get("program_name"),
        "comments": raw.get("comments"),
        "date_added": raw.get("date_added"),
        "url": raw.get("entry_url"),
        "status": raw.get("status"),
        "status_date": raw.get("status_date"),  
        "term": raw.get("term"),
        "us_or_international": raw.get("citizenship"),
        "gpa": raw.get("gpa"),
        "gre_total_score": raw.get("gre_total"),
        "gre_verbal_score": raw.get("gre_v"),
        "gre_aw_score": raw.get("gre_aw"),
        "degree": raw.get("degree_level"),
        "llm_generated_program": raw.get("llm_generated_program") or raw.get("llm-generated-program"),
        "llm_generated_university": raw.get("llm_generated_university") or raw.get("llm-generated-university"),
    }

def reset_database(dbname="studentCourses"): 
    """Drop and recreate the studentCourses database using psycopg (v3).""" 
    print(f"Resetting database '{dbname}'...") 
    
    # Connect to postgres (not the target DB) 
    conn = psycopg.connect( 
        dbname="postgres", 
        user="postgres", 
        password=os.environ.get("PGPASSWORD", "Tolkien321"), 
        host="localhost", 
        port=5432, 
        autocommit=True 
    ) 
    
    with conn.cursor() as cur: 
        # Terminate active connections 
        cur.execute(""" 
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE datname = %s; 
            """, (dbname,)) 
    
        # Drop database (must use quotes for case-sensitive name) 
        cur.execute(f'DROP DATABASE IF EXISTS "{dbname}";') 
    
        # Recreate database 
        cur.execute(f'CREATE DATABASE "{dbname}";') 

    conn.close() 
    print(f"Database '{dbname}' recreated successfully.")



# -----------------------------
# Insert a single record
# -----------------------------

def insert_record(conn, record): 
    """Insert a single applicant record, skipping duplicates.

    Uses ON CONFLICT (url) DO NOTHING to enforce uniqueness.

    Args:
        conn: Active psycopg database connection.
        record (dict): Normalized record with database column keys.

    Returns:
        int: 1 if inserted, 0 if duplicate.
    """ 
    with conn.cursor() as cur: 
        cur.execute( 
            """ 
            INSERT INTO applicants (
                program, comments, date_added, url, status, status_date, term,
                us_or_international, gpa, gre_total_score, gre_verbal_score, gre_aw_score, degree,
                llm_generated_program, llm_generated_university
            )
            VALUES (
                %(program)s, %(comments)s, %(date_added)s, %(url)s, %(status)s, %(status_date)s, %(term)s,
                %(us_or_international)s, %(gpa)s, %(gre_total_score)s, %(gre_verbal_score)s, %(gre_aw_score)s, %(degree)s,
                %(llm_generated_program)s, %(llm_generated_university)s
          )
            ON CONFLICT (url) DO NOTHING; 
                """, 
            record, 
        ) 
        conn.commit() 
        return cur.rowcount # returns 1 if inserted, 0 if duplicate



        

# -----------------------------
# Main loader
# -----------------------------
def load_into_db(filepath: str):
    """Load JSON data from a file and insert all records into PostgreSQL.

    Args:
        filepath: Path to the JSON file containing applicant records.
    """
    data = load_json(filepath)
    conn = get_connection()

    try:
        create_table(conn)

        inserted = 0

        for record in data:
            clean = normalize_record(record)
            inserted += insert_record(conn, clean)

        print(f"Inserted {inserted} new records (duplicates skipped).")

    finally:
        conn.close()

def main(drop=False): 
    """CLI entrypoint for load_data.""" 
    try: 
        if drop: 
            reset_database("studentCourses") 
        load_into_db(DATA_FILE)
        return "load_data_main_executed"
    except Exception as e: 
        print(f"Error: {e}")
        return f"error: {e}"

# ----------------------------- 
# CLI entrypoint 
# ----------------------------- 
def cli_main(args=None):
    """Parse CLI arguments and run the loader.

    Args:
        args: Optional list of CLI arguments (for testing). Defaults to sys.argv.
    """
    parser = argparse.ArgumentParser(description="Load applicant data into PostgreSQL.") 
    parser.add_argument( 
        "--drop", 
        action="store_true", 
        help="Drop and recreate the studentCourses database before loading." 
    ) 
    parsed = parser.parse_args(args) 
    main(drop=parsed.drop)


if __name__ == "__main__":  # pragma: no cover
    cli_main()

