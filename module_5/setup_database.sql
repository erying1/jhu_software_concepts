-- Module 5 Database Setup Script
-- Run this as the postgres superuser to create the gradcafe_app user and database

-- Step 1: Create database (if it doesn't exist)
-- Note: You may need to create this separately if you're not connected to template1
CREATE DATABASE "studentCourses";

-- Step 2: Connect to the studentCourses database
-- In psql: \c studentCourses

-- Step 3: Create the gradcafe_app user with a strong password
-- IMPORTANT: Replace 'your_strong_password_here' with an actual strong password
CREATE USER gradcafe_app WITH PASSWORD 'your_strong_password_here';

-- Step 4: Revoke dangerous privileges (least-privilege principle)
ALTER USER gradcafe_app NOSUPERUSER NOCREATEDB NOCREATEROLE;

-- Step 5: Grant connection permission to the database
GRANT CONNECT ON DATABASE "studentCourses" TO gradcafe_app;

-- Step 6: Grant schema usage
GRANT USAGE ON SCHEMA public TO gradcafe_app;

-- Step 7: Create the applicants table (if it doesn't exist)
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

-- Step 8: Grant table permissions (SELECT and INSERT only, no DELETE/UPDATE/DROP)
GRANT SELECT, INSERT ON TABLE applicants TO gradcafe_app;

-- Step 9: Grant sequence usage (for auto-increment p_id)
GRANT USAGE ON SEQUENCE applicants_p_id_seq TO gradcafe_app;

-- Verification: List user permissions
\du gradcafe_app

-- Verification: Show table permissions
\dp applicants
