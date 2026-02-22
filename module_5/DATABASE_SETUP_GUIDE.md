# Database Setup Guide for Module 5

## Problem
The Flask app "Update Analysis" button hangs because the database connection is not configured.

## Summary of Findings

✅ **1. PostgreSQL Server Status**: RUNNING
- PostgreSQL 18 is installed and running
- Location: `C:\Program Files\PostgreSQL\18`
- Listening on port 5432

❓ **2. Database User Status**: UNKNOWN
- Cannot verify if `gradcafe_app` user exists
- Need to connect as postgres superuser to check

⚠️ **3. Environment Variables**: NOT SET
- `.env` file created but needs your password
- Database credentials not loaded in current session

---

## Solution: 3-Step Setup

### Step 1: Find Your PostgreSQL Password

You have several options:

**Option A: Check pgAdmin (if installed)**
1. Open pgAdmin 4
2. Look at saved server connections
3. The password might be saved there

**Option B: Reset postgres password (if you don't remember it)**
1. Open Windows Services (`services.msc`)
2. Find "postgresql-x64-18" service
3. Stop the service
4. Edit `pg_hba.conf` to temporarily allow trust authentication
5. Restart service and reset password
6. Restore original pg_hba.conf

**Option C: Use the password you set during installation**
- Check any installation notes you might have saved

---

### Step 2: Create the gradcafe_app Database User

Once you can connect as `postgres`, run the setup script:

#### Method A: Using psql Command Line

```bash
# Navigate to the PostgreSQL bin directory
cd "C:\Program Files\PostgreSQL\18\bin"

# Connect as postgres superuser (you'll be prompted for password)
psql -U postgres -h localhost -p 5432

# Once connected, run:
\i C:/Users/Eric/Documents/GitHub/jhu_software_concepts/module_5/setup_database.sql
```

#### Method B: Using pgAdmin

1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Open "setup_database.sql" file
4. Execute the script

#### Method C: Manual SQL Commands

Connect to PostgreSQL and run these commands:

```sql
-- Create database
CREATE DATABASE "studentCourses";

-- Connect to it
\c studentCourses

-- Create user (CHANGE THE PASSWORD!)
CREATE USER gradcafe_app WITH PASSWORD 'YourStrongPasswordHere123!';

-- Set permissions
ALTER USER gradcafe_app NOSUPERUSER NOCREATEDB NOCREATEROLE;
GRANT CONNECT ON DATABASE "studentCourses" TO gradcafe_app;
GRANT USAGE ON SCHEMA public TO gradcafe_app;

-- Create table
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

-- Grant table permissions
GRANT SELECT, INSERT ON TABLE applicants TO gradcafe_app;
GRANT USAGE ON SEQUENCE applicants_p_id_seq TO gradcafe_app;
```

---

### Step 3: Update the .env File

Edit `.env` in the module_5 directory:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=studentCourses
DB_USER=gradcafe_app
DB_PASSWORD=YourStrongPasswordHere123!  # <-- Use the password you chose
```

**IMPORTANT:** The password in `.env` must match what you used in the `CREATE USER` command!

---

## Testing the Connection

Once setup is complete, test the connection:

```bash
cd C:\Users\Eric\Documents\GitHub\jhu_software_concepts\module_5

# Activate virtual environment
.venv\Scripts\activate

# Test database connection
python -c "from src.load_data import get_connection; conn = get_connection(); print('✓ Database connection successful!'); conn.close()"
```

---

## Starting the Flask App (After Setup)

```bash
# Set environment variables (Windows)
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=studentCourses
set DB_USER=gradcafe_app
set DB_PASSWORD=YourStrongPasswordHere123!

# Start Flask
python -m src.run
```

Or use a .env loader in your Python code (install python-dotenv if needed).

---

## Quick Verification Checklist

- [ ] PostgreSQL 18 is running (✓ Already verified)
- [ ] You can connect to PostgreSQL as postgres user
- [ ] studentCourses database exists
- [ ] gradcafe_app user exists with correct password
- [ ] applicants table exists
- [ ] gradcafe_app has SELECT, INSERT permissions on applicants
- [ ] .env file has correct password
- [ ] Environment variables are set before running Flask
- [ ] Flask app starts without errors
- [ ] "Update Analysis" button works (no more spinning wheel!)

---

## Still Having Issues?

If you're still stuck, let me know:
1. What error message you see when trying to connect
2. Whether you can open pgAdmin and connect
3. What step you're having trouble with

I can help troubleshoot further!
