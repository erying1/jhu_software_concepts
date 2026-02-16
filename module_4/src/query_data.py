
"""
query_data.py — Module 3 Analysis Queries
------------------------------------------
Provides SQL-backed analysis functions for the Grad Café dashboard.

Each ``q*`` function executes a single query against the applicants table
and returns a formatted result. :func:`get_all_analysis` aggregates all
queries into a single dictionary consumed by the Flask routes.
"""

# at top of src/query_data.py 
from src.load_data import get_connection as _real_get_connection

import sys

# Ensure module is not imported twice under different names 
sys.modules['src.query_data'] = sys.modules[__name__]


def ensure_table_exists(conn): 
    """Create the applicants table if it does not already exist.

    Args:
        conn: Active psycopg database connection.
    """
    with conn.cursor() as cur: 
        cur.execute(""" 
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
        """)
    conn.commit()

def get_connection():
    """Get a database connection with table initialization.

    Delegates to :func:`src.load_data.get_connection` and ensures the
    applicants table exists before returning.

    Returns:
        psycopg.Connection: Ready-to-use database connection.
    """
    conn = _real_get_connection() 
    ensure_table_exists(conn) 
    return conn

def _format_or_passthrough(val): 
    """Format a numeric value to two decimal places.

    Args:
        val: Value to format. Strings pass through unchanged,
             None returns ``'N/A'``, numbers are formatted to 2 decimals.

    Returns:
        str: Formatted string representation.
    """ 
    # If val is already a string (mocked tests), return it unchanged 
    if isinstance(val, str): 
        return val 
    
    # If val is None, return None
    if val is None: 
        return "N/A" 
    
    # During tests, always return raw float 
    #import os 
    #if os.getenv("PYTEST_CURRENT_TEST"): 
    #    return float(val) 
    
    # Normal runtime: format to 2 decimals
    try:
        return f"{float(val):.2f}"
    except Exception:
        return val



def q1_fall_2026_count():
    """Count applicants for Fall 2026 term.

    Returns:
        int: Number of applicants with term 'Fall 2026'.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) 
            FROM applicants 
            WHERE term='Fall 2026'
        """)
        (count,) = cur.fetchone()
        return count or 0


def q2_percent_international():
    """Calculate percentage of international applicants.

    Returns:
        float: Percentage of non-American applicants.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT AVG(CASE WHEN us_or_international != 'American' THEN 1 ELSE 0 END) * 100
            FROM applicants
        """)
        (pct,) = cur.fetchone()
        return pct or 0


def q3_average_metrics():
    """Compute average GPA and GRE scores across all applicants.

    Returns:
        dict: Keys ``avg_gpa``, ``avg_gre``, ``avg_gre_v``, ``avg_gre_aw``.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT AVG(gpa), 
                   AVG(gre_total_score), 
                   AVG(gre_verbal_score), 
                   AVG(gre_aw_score)
            FROM applicants
        """)
        row = cur.fetchone()
        avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = row
        return { 
            "avg_gpa": avg_gpa, 
            "avg_gre": avg_gre, 
            "avg_gre_v": avg_gre_v, 
            "avg_gre_aw": avg_gre_aw, 
        }


def q4_avg_gpa_american_fall_2026(): 
    """Average GPA of American applicants for Fall 2026.

    Returns:
        str: Formatted GPA to two decimals, or ``'N/A'``.
    """ 
    conn = get_connection() 
    with conn.cursor() as cur: 
        cur.execute(""" 
            SELECT AVG(gpa) 
            FROM applicants 
            WHERE us_or_international='American' AND term='Fall 2026' 
        """) 
        (val,) = cur.fetchone() 
        return _format_or_passthrough(val)


def q5_percent_accept_fall_2026():
    """Acceptance rate for Fall 2026 applicants.

    Returns:
        str: Percentage formatted to two decimals, or ``'N/A'``.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT AVG(CASE WHEN status='Accepted' THEN 1 ELSE 0 END) * 100
            FROM applicants
            WHERE term='Fall 2026'
        """)
        (val,) = cur.fetchone()
        return _format_or_passthrough(val)



def q6_avg_gpa_accept_fall_2026():
    """Average GPA of accepted Fall 2026 applicants.

    Returns:
        str: Formatted GPA to two decimals, or ``'N/A'``.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT AVG(gpa)
            FROM applicants
            WHERE status='Accepted' AND term='Fall 2026'
        """)
        (val,) = cur.fetchone()
        return _format_or_passthrough(val)



def q7_jhu_cs_masters_count():
    """Count JHU Computer Science Masters applicants.

    Returns:
        int: Number of matching applicants.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE llm_generated_university ILIKE '%Hopkins%' AND llm_generated_program ILIKE '%Computer%' AND degree ILIKE '%Master%'
        """)
        (count,) = cur.fetchone() 
        return count or 0


def q8_elite_cs_phd_accepts_2026():
    """Count accepted CS PhD applicants at elite universities for Fall 2026.

    Elite universities: Georgetown, MIT, Stanford, Carnegie Mellon.

    Returns:
        int: Number of accepted PhD applicants.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term='Fall 2026' 
                    AND degree ILIKE '%PhD%' 
                    AND llm_generated_program ILIKE '%Computer%' 
                    AND llm_generated_university IN ('Georgetown','MIT','Stanford','Carnegie Mellon') 
                    AND status='Accepted'
        """)
        (count,) = cur.fetchone() 
        return count or 0


def q9_elite_cs_phd_llm_accepts_2026():
    """Count accepted CS applicants (all degrees) at elite universities for Fall 2026.

    Uses LLM-generated program field. Elite universities: Georgetown, MIT,
    Stanford, Carnegie Mellon.

    Returns:
        int: Number of accepted applicants.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term='Fall 2026' 
                    AND llm_generated_program ILIKE '%Computer%' 
                    AND llm_generated_university IN ('Georgetown','MIT','Stanford','Carnegie Mellon') 
                    AND status='Accepted'
        """)
        (count,) = cur.fetchone() 
        return count or 0

def q10_custom(): 
    """Top 10 universities by total application count.

    Returns:
        list[tuple]: Rows of (university, count) ordered by count descending.
    """ 
    conn = get_connection() 
    with conn.cursor() as cur: 
        cur.execute(""" 
            SELECT llm_generated_university, 
                   COUNT(*) AS total_applications 
            FROM applicants 
            GROUP BY llm_generated_university 
            ORDER BY total_applications DESC 
            LIMIT 10; 
        """) 
        return cur.fetchall() 
    
def q11_custom(): 
    """Acceptance rate breakdown by degree level.

    Returns:
        list[tuple]: Rows of (degree, total, accepted, rate) ordered by rate descending.
    """ 
    conn = get_connection() 
    with conn.cursor() as cur: 
        cur.execute(""" 
                SELECT degree, 
                    COUNT(*) AS total_entries, 
                    SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END) AS total_acceptances, 
                    CASE 
                        WHEN COUNT(*) = 0 THEN 0 
                        ELSE ROUND( 
                            SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END)::numeric 
                            / COUNT(*) * 100, 2 
                        )::float 
                    END AS acceptance_rate 
                FROM applicants
                GROUP BY degree 
                ORDER BY acceptance_rate DESC; 
            """) 
        return cur.fetchall()

    
def get_all_analysis(): 
    """Run all analysis queries and return combined results.

    Returns:
        dict: All query results keyed by analysis name.
    """ 
    return { 
        "fall_2026_count": q1_fall_2026_count(), 
        "pct_international": q2_percent_international(), 
        "avg_metrics": q3_average_metrics(), 
        "avg_gpa_american_fall_2026": q4_avg_gpa_american_fall_2026(), 
        "pct_accept_fall_2026": q5_percent_accept_fall_2026(), 
        "avg_gpa_accept_fall_2026": q6_avg_gpa_accept_fall_2026(), 
        "jhu_cs_masters_count": q7_jhu_cs_masters_count(), 
        "elite_cs_phd_accepts_2026": q8_elite_cs_phd_accepts_2026(), 
        "elite_cs_phd_llm_accepts_2026": q9_elite_cs_phd_llm_accepts_2026(), 
        "top_universities": q10_custom(), 
        "degree_acceptance_summary": q11_custom(),
    }

__all__ = [ 
    "q1_fall_2026_count", 
    "q2_percent_international", 
    "q3_average_metrics", 
    "q4_avg_gpa_american_fall_2026", 
    "q5_percent_accept_fall_2026", 
    "q6_avg_gpa_accept_fall_2026", 
    "q7_jhu_cs_masters_count", 
    "q8_elite_cs_phd_accepts_2026", 
    "q9_elite_cs_phd_llm_accepts_2026", 
    "q10_custom", 
    "q11_custom", 
    "get_all_analysis", 
]



