"""
query_data.py — Module 3 Analysis Queries
------------------------------------------
Database query functions used by the Flask dashboard.

Provides SQL-backed analysis functions for the Grad Café dashboard.

Each ``q*`` function executes a single query against the applicants table
and returns a formatted result. :func:`get_all_analysis` aggregates all
queries into a single dictionary consumed by the Flask routes.
"""

import sys

# at top of src/query_data.py
from psycopg2 import sql
from src.load_data import get_connection as _real_get_connection

# Ensure module is not imported twice under different names
sys.modules["src.query_data"] = sys.modules[__name__]

# Maximum rows any multi-row query may return (enforced via LIMIT clamping)
_MAX_LIMIT = 100


def ensure_table_exists(conn):
    """Create the applicants table if it does not already exist.

    Args:
        conn: Active psycopg database connection.

    Note:
        Silently ignores permission errors, as the table may have been
        created by a superuser with appropriate privileges.
    """
    try:
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
    except Exception:  # pylint: disable=broad-exception-caught
        # Table may already exist or user lacks CREATE privilege
        # Ignore the error and proceed
        conn.rollback()


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
    # import os
    # if os.getenv("PYTEST_CURRENT_TEST"):
    #    return float(val)

    # Normal runtime: format to 2 decimals
    try:
        return f"{float(val):.2f}"
    except (ValueError, TypeError):
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
            LIMIT 1
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
            LIMIT 1
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
            LIMIT 1
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
            LIMIT 1
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
            LIMIT 1
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
            LIMIT 1
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
            WHERE llm_generated_university ILIKE '%Hopkins%'
              AND llm_generated_program ILIKE '%Computer%'
              AND degree ILIKE '%Master%'
            LIMIT 1
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
            LIMIT 1
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
            LIMIT 1
        """)
        (count,) = cur.fetchone()
        return count or 0


def q10_custom(limit=10):
    """Top universities by total application count.

    Args:
        limit (int): Rows to return, clamped to 1–100 (default 10).

    Returns:
        list[tuple]: Rows of (university, count) ordered by count descending.
    """
    limit = max(1, min(int(limit), _MAX_LIMIT))
    conn = get_connection()
    with conn.cursor() as cur:
        stmt = sql.SQL("""
            SELECT llm_generated_university,
                   COUNT(*) AS total_applications
            FROM applicants
            GROUP BY llm_generated_university
            ORDER BY total_applications DESC
            LIMIT %s
        """)
        cur.execute(stmt, (limit,))
        return cur.fetchall()


def q11_custom(limit=50):
    """Acceptance rate breakdown by degree level.

    Args:
        limit (int): Rows to return, clamped to 1–100 (default 50).

    Returns:
        list[tuple]: Rows of (degree, total, accepted, rate) ordered by rate descending.
    """
    limit = max(1, min(int(limit), _MAX_LIMIT))
    conn = get_connection()
    with conn.cursor() as cur:
        stmt = sql.SQL("""
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
            ORDER BY acceptance_rate DESC
            LIMIT %s
        """)
        cur.execute(stmt, (limit,))
        return cur.fetchall()


def get_all_analysis():
    """Run all analysis queries and return combined results.

    Returns:
        dict: All query results keyed by analysis name. Includes both canonical
        keys and template-facing aliases for backward compatibility.
    """
    fall_2026_count = q1_fall_2026_count()
    pct_international = q2_percent_international()
    avg_metrics = q3_average_metrics()
    avg_gpa_american = q4_avg_gpa_american_fall_2026()
    pct_accept_fall_2026 = q5_percent_accept_fall_2026()
    avg_gpa_accept_fall_2026 = q6_avg_gpa_accept_fall_2026()
    jhu_cs_masters = q7_jhu_cs_masters_count()
    elite_cs_phd = q8_elite_cs_phd_accepts_2026()
    elite_cs_phd_llm = q9_elite_cs_phd_llm_accepts_2026()
    top_universities = q10_custom()
    degree_summary = q11_custom()
    return {
        "fall_2026_count": fall_2026_count,
        "pct_international": pct_international,
        "avg_metrics": avg_metrics,
        "avg_gpa_american_fall_2026": avg_gpa_american,
        "avg_gpa_american": avg_gpa_american,
        "pct_accept_fall_2026": pct_accept_fall_2026,
        "avg_gpa_accept_fall_2026": avg_gpa_accept_fall_2026,
        "jhu_cs_masters_count": jhu_cs_masters,
        "jhu_cs_masters": jhu_cs_masters,
        "elite_cs_phd_accepts_2026": elite_cs_phd,
        "top_schools_accept": elite_cs_phd,
        "elite_cs_phd_llm_accepts_2026": elite_cs_phd_llm,
        "top_schools_accept_llm": elite_cs_phd_llm,
        "top_universities": top_universities,
        "degree_acceptance_summary": degree_summary,
        "acceptance_by_degree": degree_summary,
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
