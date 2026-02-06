# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#
# load_data.py

# Overview of load_data.py:
#
# 
# Input file: TBD
# Output file: TBD

# load_data.py
#
# How to start postgres locally (Windows):
# C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres


import json
from pathlib import Path
import psycopg

# -----------------------------
# Load JSON from disk
# -----------------------------
def load_json(filepath: str):
    file_path = Path(filepath)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# Connect to PostgreSQL
# -----------------------------
def get_connection():
    return psycopg.connect(
        dbname="studentCourses",
        user="postgres",
        password="Tolkien321",
        host="localhost",
        port=5432,
    )


# -----------------------------
# Create applicants table
# -----------------------------
def create_table(conn):
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
        """
    )
    conn.commit()
                                   
def normalize_record(raw):
    return {
        "program": raw.get("program") or raw.get("program_name"),
        "comments": raw.get("comments"),
        "date_added": raw.get("date_added"),
        "url": raw.get("entry_url"),
        "status": raw.get("status"),
        "term": raw.get("term"),
        "us_or_international": raw.get("citizenship"),
        "gpa": raw.get("gpa"),
        "gre": raw.get("gre_total"),
        "gre_v": raw.get("gre_v"),
        "gre_aw": raw.get("gre_aw"),
        "degree": raw.get("degree_level"),
        "llm_generated_program": raw.get("llm_generated_program") or raw.get("llm-generated-program"),
        "llm_generated_university": raw.get("llm_generated_university") or raw.get("llm-generated-university"),
    }



# -----------------------------
# Insert a single record
# -----------------------------

def insert_record(conn, record): 
    with conn.cursor() as cur: 
        cur.execute( 
            """ 
            INSERT INTO applicants ( 
                program, comments, date_added, url, status, term, 
                us_or_international, gpa, gre, gre_v, gre_aw, degree, 
                llm_generated_program, llm_generated_university 
            ) 
            VALUES ( 
                %(program)s, %(comments)s, %(date_added)s, %(url)s, %(status)s, %(term)s, 
                %(us_or_international)s, %(gpa)s, %(gre)s, %(gre_v)s, %(gre_aw)s, %(degree)s, 
                %(llm_generated_program)s, %(llm_generated_university)s ) 
            ON CONFLICT (url) DO NOTHING; 
                """, 
            record, 
        ) 
        conn.commit() 
        return cur.rowcount # ⭐ returns 1 if inserted, 0 if duplicate



        

# -----------------------------
# Main loader
# -----------------------------
def load_into_db(filepath: str):
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


# -----------------------------
# CLI entrypoint
# -----------------------------
if __name__ == "__main__":
    try:
        load_into_db("../module_2/llm_extend_applicant_data.json")
    except Exception as e:
        print(f"Error: {e}")
