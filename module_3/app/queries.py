# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#
"""
queries.py — Module 3 SQL Query Layer
-------------------------------------
This module contains all SQL queries used by the Flask dashboard. It provides a
clean separation between application logic (routes.py) and database logic.

Key responsibilities:
• Open PostgreSQL connections.
• Execute parameterized SQL queries safely.
• Compute statistics for the dashboard:
  – applicant counts
  – GPA/GRE averages
  – acceptance rates
  – Fall 2026 metrics
  – university‑level and degree‑level summaries
• Return results in Python‑friendly structures for rendering.

This file centralizes all database access for maintainability and clarity.
"""

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

def safe(val):
    return val if val is not None else "N/A"

def get_diagnostics(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants;")
        (total,) = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM applicants WHERE gpa IS NOT NULL;")
        (gpa_present,) = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM applicants WHERE gre IS NOT NULL;")
        (gre_present,) = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international IS NOT NULL;")
        (cit_present,) = cur.fetchone()

    return {
        "total": total,
        "gpa_present": gpa_present,
        "gre_present": gre_present,
        "cit_present": cit_present,
        "gpa_missing": total - gpa_present,
        "gre_missing": total - gre_present,
        "cit_missing": total - cit_present,
    }

def get_all_results():
    conn = get_connection()
    try:
        metrics = q3_average_metrics(conn)
        
        # Format metrics for display
        formatted_metrics = { 
            'avg_gpa': safe(metrics['avg_gpa']), 
            'avg_gre': safe(metrics['avg_gre']), 
            'avg_gre_v': safe(metrics['avg_gre_v']), 
            'avg_gre_aw': safe(metrics['avg_gre_aw']), 
        }

        

        return {
            "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p"),
            "fall_2026_count": q1_fall_2026_count(conn),
            "pct_international": q2_percent_international(conn),
            "avg_metrics": formatted_metrics,
            "avg_gpa_american": q4_avg_gpa_american_fall_2026(conn),
            "pct_accept_fall_2026": q5_percent_accept_fall_2026(conn),
            "avg_gpa_accept_fall_2026": q6_avg_gpa_accept_fall_2026(conn),
            "jhu_cs_masters": q7_jhu_cs_masters(conn),
            "top_schools_accept": q8_top_schools_phd_accept(conn),
            "top_schools_accept_llm": q9_llm_top_schools_phd_accept(conn),

            # My two additional queries:
            "top_universities": q10_custom(conn), 
            "acceptance_by_degree": q11_custom(conn),

            # ⭐ NEW: Diagnostics "diagnostics": 
            "diagnostics": get_diagnostics(conn),

        }
    finally:
        conn.close()

def q10_custom(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT llm_generated_university, COUNT(*) AS total_applications
            FROM applicants
            GROUP BY llm_generated_university
            ORDER BY total_applications DESC
            LIMIT 10;
        """)
        return cur.fetchall()

def q11_custom(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                degree,
                COUNT(*) AS total_entries,
                SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END) AS total_acceptances,
                ROUND(
                    SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END)::numeric 
                    / COUNT(*) * 100, 2
                ) AS acceptance_rate
            FROM applicants
            GROUP BY degree
            ORDER BY acceptance_rate DESC;
        """)
        return cur.fetchall()
    
def compute_scraper_diagnostics(records):
    total = len(records)

    def count(field):
        return sum(1 for r in records if r.get(field) not in (None, "", "null"))

    diagnostics = {
        "Total scraped rows": total,
        "Comments present": count("comments"),
        "Term present": count("term"),
        "Citizenship present": count("citizenship"),
        "GPA present": count("gpa"),
        "GRE Total present": count("gre_total"),
        "GRE Verbal present": count("gre_v"),
        "GRE AW present": count("gre_aw"),
    }

    # Missing counts
    diagnostics.update({
        "Comments missing": total - diagnostics["Comments present"],
        "Term missing": total - diagnostics["Term present"],
        "Citizenship missing": total - diagnostics["Citizenship present"],
        "GPA missing": total - diagnostics["GPA present"],
        "GRE Total missing": total - diagnostics["GRE Total present"],
        "GRE Verbal missing": total - diagnostics["GRE Verbal present"],
        "GRE AW missing": total - diagnostics["GRE AW present"],
    })

    return diagnostics
