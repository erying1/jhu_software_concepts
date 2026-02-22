# Final Setup Steps - Almost There!

## ✅ **What's Working**
- PostgreSQL 18 is running
- `gradcafe_app` user exists (password: `test1234`)
- Database connection from Python works
- Flask app loads successfully

## ⚠️ **What's Missing**
- `applicants` table doesn't exist (or gradcafe_app can't create it)
- Need to create the table as postgres superuser

---

## 🎯 **Final Step: Create the Applicants Table**

You have **3 options**:

### Option 1: Using pgAdmin (Easiest)

1. Open **pgAdmin 4**
2. Connect to your PostgreSQL server
3. Navigate to: Servers → PostgreSQL 18 → Databases → studentCourses
4. Right-click "studentCourses" → Query Tool
5. Open file: `create_table.sql`
6. Click "Execute" (▶ button)
7. Done!

### Option 2: Using psql Command Line

```bash
# Navigate to PostgreSQL bin directory
cd "C:\Program Files\PostgreSQL\18\bin"

# Connect as postgres user (enter your postgres password when prompted)
psql -U postgres -h localhost -d studentCourses

# Then in the psql prompt, run:
\i C:/Users/Eric/Documents/GitHub/jhu_software_concepts/module_5/create_table.sql

# Exit psql
\q
```

### Option 3: Manual SQL Commands

If you can connect to PostgreSQL any other way, just run these commands:

```sql
-- Connect to studentCourses database first
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

GRANT SELECT, INSERT ON TABLE applicants TO gradcafe_app;
GRANT USAGE ON SEQUENCE applicants_p_id_seq TO gradcafe_app;
```

---

## 🚀 **After Creating the Table**

Once the table is created, start the Flask app:

### Quick Start (Double-click this file)
```
run_flask.bat
```

### Or Manually
```bash
cd C:\Users\Eric\Documents\GitHub\jhu_software_concepts\module_5

# Set environment variables
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=studentCourses
set DB_USER=gradcafe_app
set DB_PASSWORD=test1234

# Activate virtual environment
.venv\Scripts\activate

# Start Flask
python -m src.run
```

### Then Test
1. Open browser: http://localhost:8080
2. Click "Update Analysis" button
3. **It should work instantly now** (no more spinning wheel!)

---

## 🔍 **Verify Table Creation**

After running the SQL commands, verify the table exists:

```sql
-- In psql or pgAdmin:
\dt applicants

-- Check permissions:
\dp applicants

-- Should show:
-- gradcafe_app | SELECT, INSERT
```

---

## 📝 **Summary of What We Fixed**

### The Problem:
- "Update Analysis" button hung forever (spinning wheel)

### Root Cause:
- Environment variables not set → Database connection timed out

### The Solution (3 parts):
1. ✅ Set DB credentials in `.env` file (DB_PASSWORD=test1234)
2. ✅ Created `run_flask.bat` to set environment variables
3. ⏳ **Next**: Create applicants table (you're here!)

### After This Step:
- Flask app will connect to database successfully
- All 11 SQL queries will run instantly
- "Update Analysis" button will work
- No more hanging/spinning!

---

## 💡 **Need Help?**

If you're stuck:
1. Can you open pgAdmin and connect to your server?
2. What's your postgres user password? (different from gradcafe_app)
3. Let me know what error you see!

**You're almost done - just one SQL script away from a working app!** 🎉
