# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#
# queries

# Overview of queries.py
#
# This file wraps your SQL queries so the Flask page can call them and get structured results.
# It imports your logic from query_data.py but returns values instead of printing.

# Input file: TBD
# Output file: TBD

# app/queries.py

import psycopg
from datetime import datetime
from query_data import (
    q1_fall_2026_count,
    q2_percent_international,
    q3_average_metrics,
    q4_avg_gpa_american_fall_2026,
    q5_percent_accept_fall_2026,
    q6_avg_gpa_accept_fall_2026,
    q7_jhu_cs_masters,
    q8_top_schools_phd_accept,
    q9_llm_top_schools_phd_accept,
    q10_custom,
    q11_custom,
)

def get_connection():
    return psycopg.connect(
        dbname="studentCourses",
        user="postgres",
        password="Tolkien321",
        host="localhost",
        port=5432,
    )

def get_all_results():
    conn = get_connection()
    try:
        return {
            "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p"),
            "fall_2026_count": q1_fall_2026_count(conn),
            "pct_international": q2_percent_international(conn),
            "avg_metrics": q3_average_metrics(conn),
            "avg_gpa_american": q4_avg_gpa_american_fall_2026(conn),
            "pct_accept_fall_2026": q5_percent_accept_fall_2026(conn),
            "avg_gpa_accept_fall_2026": q6_avg_gpa_accept_fall_2026(conn),
            "jhu_cs_masters": q7_jhu_cs_masters(conn),
            "top_schools_accept": q8_top_schools_phd_accept(conn),
            "top_schools_accept_llm": q9_llm_top_schools_phd_accept(conn),
            "custom1": q10_custom(conn),
            "custom2": q11_custom(conn),
        }
    finally:
        conn.close()
