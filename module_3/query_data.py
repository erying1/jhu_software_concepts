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
# Q1 – How many entries applied for Fall 2026?
# ------------------------------------------------------------
def q1_fall_2026_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term ILIKE '%Fall 2026%' 
               OR term ILIKE '%F26%'
               OR term ILIKE '%Fall26%';
        """)
        (count,) = cur.fetchone()

    print("\nQ1: How many entries applied for Fall 2026?")
    print(f"Answer: {count}")
    return count


# ------------------------------------------------------------
# Q2 – Percent international (not American or Other)
# ------------------------------------------------------------
def q2_percent_international(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE us_or_international = 'International')
                    / NULLIF(COUNT(*) FILTER (WHERE us_or_international IS NOT NULL), 0),
                    2
                ) AS pct_international
            FROM applicants;
        """)
        (pct,) = cur.fetchone()

    print("\nQ2: Percent of entries from international students")
    print(f"Answer: {fmt(pct)}%")
    return pct if pct is not None else 0.0


# ------------------------------------------------------------
# Q3 – Average GPA, GRE, GRE V, GRE AW
# FIXED: Proper cursor handling for multiple queries
# ------------------------------------------------------------
def q3_average_metrics(conn):
    # Calculate each metric separately with its own cursor
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ROUND(AVG(gpa)::numeric, 2) 
            FROM applicants 
            WHERE gpa IS NOT NULL AND gpa > 0;
        """)
        avg_gpa = cur.fetchone()[0]
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ROUND(AVG(gre)::numeric, 2) 
            FROM applicants 
            WHERE gre IS NOT NULL AND gre > 0;
        """)
        avg_gre = cur.fetchone()[0]
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ROUND(AVG(gre_v)::numeric, 2) 
            FROM applicants 
            WHERE gre_v IS NOT NULL AND gre_v > 0;
        """)
        avg_gre_v = cur.fetchone()[0]
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ROUND(AVG(gre_aw)::numeric, 2) 
            FROM applicants 
            WHERE gre_aw IS NOT NULL AND gre_aw > 0;
        """)
        avg_gre_aw = cur.fetchone()[0]
    
    print("\nQ3: Average GPA, GRE, GRE V, GRE AW")
    print(f"GPA: {fmt(avg_gpa)}")
    print(f"GRE: {fmt(avg_gre)}")
    print(f"GRE V: {fmt(avg_gre_v)}")
    print(f"GRE AW: {fmt(avg_gre_aw)}")
    
    return {
        'avg_gpa': avg_gpa,
        'avg_gre': avg_gre,
        'avg_gre_v': avg_gre_v,
        'avg_gre_aw': avg_gre_aw
    }


# ------------------------------------------------------------
# Q4 – Average GPA of American students in Fall 2026
# ------------------------------------------------------------
def q4_avg_gpa_american_fall_2026(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ROUND(AVG(gpa)::numeric, 2) AS avg_gpa
            FROM applicants
            WHERE (term ILIKE '%Fall 2026%' OR term ILIKE '%F26%' OR term ILIKE '%Fall26%')
              AND us_or_international = 'American'
              AND gpa IS NOT NULL 
              AND gpa > 0;
        """)
        (avg_gpa,) = cur.fetchone()

    print("\nQ4: Average GPA of American students in Fall 2026")
    print(f"Answer: {fmt(avg_gpa)}")
    return avg_gpa


# ------------------------------------------------------------
# Q5 – Percent of Fall 2026 entries that are Acceptances
# ------------------------------------------------------------
def q5_percent_accept_fall_2026(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE status = 'Accepted')
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS pct_accept
            FROM applicants
            WHERE term ILIKE '%Fall 2026%' 
               OR term ILIKE '%F26%'
               OR term ILIKE '%Fall26%';
        """)
        (pct,) = cur.fetchone()

    print("\nQ5: Percent of Fall 2026 entries that are Acceptances")
    print(f"Answer: {fmt(pct)}%")
    return pct if pct is not None else 0.0


# ------------------------------------------------------------
# Q6 – Average GPA of Fall 2026 Acceptances
# ------------------------------------------------------------
def q6_avg_gpa_accept_fall_2026(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ROUND(AVG(gpa)::numeric, 2) AS avg_gpa
            FROM applicants
            WHERE (term ILIKE '%Fall 2026%' OR term ILIKE '%F26%' OR term ILIKE '%Fall26%')
              AND status = 'Accepted'
              AND gpa IS NOT NULL
              AND gpa > 0;
        """)
        (avg_gpa,) = cur.fetchone()

    print("\nQ6: Average GPA of Fall 2026 Acceptances")
    print(f"Answer: {fmt(avg_gpa)}")
    return avg_gpa


# ------------------------------------------------------------
# Q7 – Count of entries applying to JHU CS Masters
# ------------------------------------------------------------
def q7_jhu_cs_masters(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE (
                    llm_generated_program ILIKE '%Hopkins%' OR
                    llm_generated_program ILIKE '%JHU%' OR
                    llm_generated_university ILIKE '%Johns Hopkins%'
                  )
              AND (
                    llm_generated_program ILIKE '%Computer%' OR
                    llm_generated_program ILIKE '%CS%' OR
                    llm_generated_program ILIKE '%Computer Science%'
                  )
              AND (degree ILIKE '%Master%' OR degree ILIKE '%MS%' OR degree ILIKE '%M.S.%');
        """)
        (count,) = cur.fetchone()

    print("\nQ7: How many entries applied to JHU for a Masters in CS?")
    print(f"Answer: {count}")
    return count


# ------------------------------------------------------------
# Q8 – Acceptances to Georgetown/MIT/Stanford/CMU for CS PhD (2026)
# ------------------------------------------------------------
def q8_top_schools_phd_accept(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term ILIKE '%2026%'
              AND status = 'Accepted'
              AND degree ILIKE '%PhD%'
              AND (llm_generated_program ILIKE '%Computer%' OR llm_generated_program ILIKE '%CS%')
              AND (
                    llm_generated_university ILIKE '%Georgetown%' OR
                    llm_generated_university ILIKE '%MIT%' OR
                    llm_generated_university ILIKE '%Massachusetts Institute of Technology%' OR
                    llm_generated_university ILIKE '%Stanford%' OR
                    llm_generated_university ILIKE '%Carnegie Mellon%'
                  );
        """)
        (count,) = cur.fetchone()

    print("\nQ8: Acceptances to Georgetown/MIT/Stanford/CMU for CS PhD (2026)")
    print(f"Answer: {count}")
    return count


# ------------------------------------------------------------
# Q9 – Same as Q8 but using LLM-generated fields
# ------------------------------------------------------------
def q9_llm_top_schools_phd_accept(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term ILIKE '%2026%'
              AND status = 'Accepted'
              AND degree ILIKE '%PhD%'
              AND (llm_generated_program ILIKE '%Computer%' OR llm_generated_program ILIKE '%CS%')
              AND (
                    llm_generated_university ILIKE '%Georgetown%' OR
                    llm_generated_university ILIKE '%MIT%' OR
                    llm_generated_university ILIKE '%Massachusetts Institute of Technology%' OR
                    llm_generated_university ILIKE '%Stanford%' OR
                    llm_generated_university ILIKE '%Carnegie Mellon%'
              );
        """)
        (count,) = cur.fetchone()

    print("\nQ9: Same as Q8 but using LLM-generated fields")
    print(f"Answer: {count}")
    return count


# ------------------------------------------------------------
# Q10 – Custom Question 1: Average GPA by nationality
# ------------------------------------------------------------
def q10_custom(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                us_or_international AS nationality,
                COUNT(*) AS total_applicants,
                ROUND(AVG(gpa)::numeric, 2) AS avg_gpa
            FROM applicants
            WHERE us_or_international IS NOT NULL
              AND gpa > 0
            GROUP BY us_or_international
            ORDER BY avg_gpa DESC NULLS LAST;
        """)
        rows = cur.fetchall()

    print("\nQ10 (Custom): Average GPA by nationality")
    print("(Shows if certain nationalities have higher academic metrics)")
    for nationality, count, avg_gpa in rows:
        print(f"  {nationality}: {count} applicants, avg GPA = {fmt(avg_gpa)}")
    return rows


# ------------------------------------------------------------
# Q11 – Custom Question 2: Acceptance rate by degree type
# ------------------------------------------------------------
def q11_custom(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                degree,
                COUNT(*) AS total_applicants,
                COUNT(*) FILTER (WHERE status = 'Accepted') AS acceptances,
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE status = 'Accepted') 
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS acceptance_rate
            FROM applicants
            WHERE degree IS NOT NULL
            GROUP BY degree
            ORDER BY total_applicants DESC;
        """)
        rows = cur.fetchall()

    print("\nQ11 (Custom): Applicant count and acceptance rate by degree type")
    print("(Shows which degree programs are most popular and competitive)")
    for degree, count, accepts, rate in rows:
        print(f"  {degree}: {count} applicants, {accepts} accepted ({fmt(rate)}%)")
    return rows


# ------------------------------------------------------------
# Debug function: Check data quality
# ------------------------------------------------------------
def debug_gpa_presence(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE gpa IS NOT NULL;")
        (total_gpa,) = cur.fetchone()
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE gpa > 0;")
        (real_gpa,) = cur.fetchone()

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants;")
        (total,) = cur.fetchone()

    pct_total = (total_gpa * 100 / total) if total > 0 else 0
    pct_real = (real_gpa * 100 / total) if total > 0 else 0
    
    print(f"\nDebug: GPA Analysis")
    print(f"  Total entries: {total}")
    print(f"  GPA not null: {total_gpa} ({pct_total:.1f}%)")
    print(f"  GPA > 0: {real_gpa} ({pct_real:.1f}%)")
    print(f"  GPA = 0: {total_gpa - real_gpa} (excluded from averages)")
    
    if real_gpa == 0:
        print("  ⚠️ WARNING: No valid GPA data (all 0 or null)!")


# ------------------------------------------------------------
# Diagnostics function: Check all field coverage
# ------------------------------------------------------------
def diagnostics(conn): 
    with conn.cursor() as cur: 
        cur.execute("SELECT COUNT(*) FROM applicants;") 
        (total,) = cur.fetchone() 
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE gpa IS NOT NULL AND gpa > 0;") 
        (gpa_present,) = cur.fetchone() 
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE gre IS NOT NULL AND gre > 0;") 
        (gre_present,) = cur.fetchone() 
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE gre_v IS NOT NULL AND gre_v > 0;") 
        (gre_v_present,) = cur.fetchone() 
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE us_or_international IS NOT NULL;") 
        (cit_present,) = cur.fetchone()
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE term IS NOT NULL AND term != '';")
        (term_present,) = cur.fetchone()
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM applicants WHERE comments IS NOT NULL AND comments != '' AND comments NOT LIKE '%estimated%';")
        (comments_present,) = cur.fetchone()
    
    return { 
        "total": total, 
        "gpa_present": gpa_present, 
        "gre_present": gre_present,
        "gre_v_present": gre_v_present,
        "cit_present": cit_present,
        "term_present": term_present,
        "comments_present": comments_present,
    }


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("\n" + "="*60)
    print("=== Running Module 3 Queries ===")
    print("="*60)
    
    conn = get_connection()
    try:
        # Run all queries
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

        # Debug info
        print("\n" + "="*60)
        print("=== Diagnostics ===")
        print("="*60)
        debug_gpa_presence(conn)
        
        diag = diagnostics(conn)
        print(f"\nData Coverage (excluding 0 values):")
        print(f"  Total entries: {diag['total']}")
        print(f"  Term present: {diag['term_present']} ({diag['term_present']*100//diag['total'] if diag['total'] > 0 else 0}%)")
        print(f"  Citizenship present: {diag['cit_present']} ({diag['cit_present']*100//diag['total'] if diag['total'] > 0 else 0}%)")
        print(f"  GPA > 0: {diag['gpa_present']} ({diag['gpa_present']*100//diag['total'] if diag['total'] > 0 else 0}%)")
        print(f"  GRE > 0: {diag['gre_present']} ({diag['gre_present']*100//diag['total'] if diag['total'] > 0 else 0}%)")
        print(f"  GRE V > 0: {diag['gre_v_present']} ({diag['gre_v_present']*100//diag['total'] if diag['total'] > 0 else 0}%)")
        print(f"  Real comments: {diag['comments_present']} ({diag['comments_present']*100//diag['total'] if diag['total'] > 0 else 0}%)")

    finally:
        conn.close()
    
    print("\n" + "="*60)
    print("=== Query execution complete ===")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
