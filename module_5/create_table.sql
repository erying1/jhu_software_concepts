-- Run this script as the postgres superuser
-- This creates the applicants table and grants permissions to gradcafe_app

-- Make sure you're connected to the studentCourses database first
-- In psql: \c studentCourses

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

-- Grant permissions to gradcafe_app (SELECT and INSERT only)
GRANT SELECT, INSERT ON TABLE applicants TO gradcafe_app;
GRANT USAGE ON SEQUENCE applicants_p_id_seq TO gradcafe_app;

-- Verify the table was created
SELECT COUNT(*) AS row_count FROM applicants;

-- Verify permissions
\dp applicants
