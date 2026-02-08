# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment
#
# query_data.py

import psycopg

def get_connection():
    """Connect to PostgreSQL database."""
    return psycopg.connect(
        dbname="studentCourses",
        user="postgres",
        password="Tolkien321",
        host="localhost",
        port=5432,
    )


# ------------------------------------------------------------
# Helper: format numbers safely
# ------------------------------------------------------------
def fmt(value):
    """Format floats to 2 decimals or return 'N/A'."""
    return f"{value:.2f}" if value is not None else "N/A"


# ------------------------------------------------------------
# Q1 — How many entries applied for Fall 2026?
# ------------------------------------------------------------
def q1_fall_2026_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term = 'Spring 2026';
        """)
        (count,) = cur.fetchone()

    print("\nQ1: How many entries applied for Fall 2026?")
    print(f"Answer: {count}")
    return count


# ------------------------------------------------------------
# Q2 — Percent international (not American or Other)
# ------------------------------------------------------------
def q2_percent_international(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                100.0 * SUM(CASE WHEN us_or_international NOT IN ('American', 'Other') 
                                 AND us_or_international IS NOT NULL
                                 THEN 1 ELSE 0 END)
                / COUNT(*) AS pct_international
            FROM applicants;
        """)
        (pct,) = cur.fetchone()

    print("\nQ2: Percent of entries from international students")
    print(f"Answer: {fmt(pct)}%")
    return pct


# ------------------------------------------------------------
# Q3 — Average GPA, GRE, GRE V, GRE AW
# ------------------------------------------------------------
def q3_average_metrics(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                AVG(gpa),
                AVG(gre),
                AVG(gre_v),
                AVG(gre_aw)
            FROM applicants;
        """)
        row = cur.fetchone()

    # If row is None, return safe defaults 
    if row is None: 
        return (None, None, None, None)

    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = row

    print("\nQ3: Average GPA, GRE, GRE V, GRE AW")
    print(f"GPA: {fmt(avg_gpa)}")
    print(f"GRE: {fmt(avg_gre)}")
    print(f"GRE V: {fmt(avg_gre_v)}")
    print(f"GRE AW: {fmt(avg_gre_aw)}")
    return row


# ------------------------------------------------------------
# Q4 — Average GPA of American students in Fall 2026
# ------------------------------------------------------------
def q4_avg_gpa_american_fall_2026(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT AVG(gpa)
            FROM applicants
            WHERE term = 'Fall 2026'
              AND us_or_international = 'American'
              AND gpa IS NOT NULL;
        """)
        (avg_gpa,) = cur.fetchone()

    print("\nQ4: Average GPA of American students in Fall 2026")
    print(f"Answer: {fmt(avg_gpa)}")
    return avg_gpa


# ------------------------------------------------------------
# Q5 — Percent of Fall 2026 entries that are Acceptances
# ------------------------------------------------------------
def q5_percent_accept_fall_2026(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                100.0 * SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END)
                / COUNT(*) AS pct_accept
            FROM applicants
            WHERE term = 'Fall 2026';
        """)
        (pct,) = cur.fetchone()

    print("\nQ5: Percent of Fall 2026 entries that are Acceptances")
    print(f"Answer: {fmt(pct)}%")
    return pct


# ------------------------------------------------------------
# Q6 — Average GPA of Fall 2026 Acceptances
# ------------------------------------------------------------
def q6_avg_gpa_accept_fall_2026(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT AVG(gpa)
            FROM applicants
            WHERE term = 'Fall 2026'
              AND status = 'Accepted'
              AND gpa IS NOT NULL;
        """)
        (avg_gpa,) = cur.fetchone()

    print("\nQ6: Average GPA of Fall 2026 Acceptances")
    print(f"Answer: {fmt(avg_gpa)}")
    return avg_gpa


# ------------------------------------------------------------
# Q7 — Count of entries applying to JHU CS Masters
# ------------------------------------------------------------
def q7_jhu_cs_masters(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE (
                    program ILIKE '%Hopkins%' OR
                    program ILIKE '%JHU%' OR
                    llm_generated_university = 'Johns Hopkins University'
                  )
              AND (
                    program ILIKE '%Computer%' OR
                    program ILIKE '%CS%' OR
                    llm_generated_program ILIKE '%Computer%'
                  )
              AND degree ILIKE '%M%';
        """)
        (count,) = cur.fetchone()

    print("\nQ7: How many entries applied to JHU for a Masters in CS?")
    print(f"Answer: {count}")
    return count


# ------------------------------------------------------------
# Q8 — Acceptances to Georgetown/MIT/Stanford/CMU for CS PhD (Fall 2026)
# ------------------------------------------------------------
def q8_top_schools_phd_accept(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term = 'Fall 2026'
              AND status = 'Accepted'
              AND degree ILIKE '%PhD%'
              AND program ILIKE '%Computer%'
              AND (
                    program ILIKE '%Georgetown%' OR
                    program ILIKE '%MIT%' OR
                    program ILIKE '%Massachusetts Institute of Technology%' OR
                    program ILIKE '%Stanford%' OR
                    program ILIKE '%Carnegie Mellon%'
                  );
        """)
        (count,) = cur.fetchone()

    print("\nQ8: Acceptances to Georgetown/MIT/Stanford/CMU for CS PhD (Fall 2026)")
    print(f"Answer: {count}")
    return count


# ------------------------------------------------------------
# Q9 — Same as Q8 but using LLM-generated fields
# ------------------------------------------------------------
def q9_llm_top_schools_phd_accept(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term = 'Fall 2026'
              AND status = 'Accepted'
              AND degree ILIKE '%PhD%'
              AND llm_generated_program ILIKE '%Computer%'
              AND llm_generated_university IN (
                    'Georgetown University',
                    'Massachusetts Institute of Technology',
                    'Stanford University',
                    'Carnegie Mellon University'
              );
        """)
        (count,) = cur.fetchone()

    print("\nQ9: Same as Q8 but using LLM-generated fields")
    print(f"Answer: {count}")
    return count


# ------------------------------------------------------------
# Q10 — Custom Question 1
# ------------------------------------------------------------
def q10_custom(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                us_or_international,
                AVG(gpa)
            FROM applicants
            WHERE gpa IS NOT NULL
            GROUP BY us_or_international;
        """)
        rows = cur.fetchall()

    print("\nQ10 (Custom): Average GPA by nationality")
    for nationality, avg_gpa in rows:
        print(f"{nationality}: {fmt(avg_gpa)}")
    return rows


# ------------------------------------------------------------
# Q11 — Custom Question 2
# ------------------------------------------------------------
def q11_custom(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                degree,
                COUNT(*)
            FROM applicants
            GROUP BY degree
            ORDER BY COUNT(*) DESC;
        """)
        rows = cur.fetchall()

    print("\nQ11 (Custom): Count of applicants by degree type")
    for degree, count in rows:
        print(f"{degree}: {count}")
    return rows

def debug_gpa_presence(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE gpa IS NOT NULL;")
        (non_null,) = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM applicants;")
        (total,) = cur.fetchone()

    print(f"\nDebug: GPA present in {non_null} of {total} rows")

def diagnostics(conn): 
    with conn.cursor() as cur: 
        cur.execute("SELECT COUNT(*) FROM applicants;") 
        (total,) = cur.fetchone() 
        
        cur.execute("SELECT COUNT(*) FROM applicants WHERE gpa IS NOT NULL;") 
        (gpa_present,) = cur.fetchone() 
        
        cur.execute("SELECT COUNT(*) FROM applicants WHERE gre IS NOT NULL;") 
        (gre_present,) = cur.fetchone() 
        
        cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international IS NOT NULL;") 
        (cit_present,) = cur.fetchone() 
    return { "total": total, 
            "gpa_present": gpa_present, 
            "gre_present": gre_present, 
            "cit_present": cit_present, 
            }

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("\n=== Running Module 3 Queries ===\n")
    conn = get_connection()
    try:
        q1_fall_2026_count(conn)
        q2_percent_international(conn)
        q3_average_metrics(conn)
        q4_avg_gpa_american_fall_2026(conn)
        q5_percent_accept_fall_2026(conn)
        q6_avg_gpa_accept_fall_2026(conn)
        q7_jhu_cs_masters(conn)
        q8_top_schools_phd_accept(conn)
        q9_llm_top_schools_phd_accept(conn)
        q10_custom(conn)
        q11_custom(conn)

        debug_gpa_presence(conn)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
