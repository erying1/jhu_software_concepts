# Flask Startup Guide - IMPORTANT!

## ⚠️ Common Issue: "File not found" Error

If you see this error:
```
{
  "error": "Error during data pull: [WinError 2] The system cannot find the file specified",
  "ok": false
}
```

**Root Cause:** Flask is not running with the virtual environment activated.

---

## ✅ CORRECT WAY to Start Flask

### Method 1: Use START_FLASK_HERE.bat (Recommended)

**Double-click this file:** `START_FLASK_HERE.bat`

This script:
1. ✓ Sets database credentials
2. ✓ Activates virtual environment  
3. ✓ Uses venv Python (with all dependencies)
4. ✓ Starts Flask correctly

### Method 2: Use run_flask.bat

**Double-click:** `run_flask.bat`

Same as Method 1, just a shorter name.

### Method 3: Manual (Command Line)

```bash
cd C:\Users\Eric\Documents\GitHub\jhu_software_concepts\module_5

# Set environment variables
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=studentCourses
set DB_USER=gradcafe_app
set DB_PASSWORD=test1234

# Activate venv
.venv\Scripts\activate

# Start Flask (from within venv)
python -m src.run
```

---

## ❌ WRONG WAYS (Will Fail!)

### Don't do this:
```bash
# ❌ WRONG: Running without venv
python -m src.run

# ❌ WRONG: System Python
C:\Python314\python.exe -m src.run

# ❌ WRONG: No database credentials
python -m src.run  # (without setting DB_* variables)
```

---

## 🔍 How to Tell if Flask is Running Correctly

When Flask starts, you should see:

```
✓ Virtual environment: .venv\Scripts\python.exe
✓ Database credentials set
✓ Flask running on http://127.0.0.1:8080
```

Then when you click "Pull Data", it should:
1. Find the scraper script
2. Run with venv Python (has beautifulsoup4)
3. Successfully scrape data

---

## 🐛 Still Getting Errors?

### Check 1: Is venv activated?
```bash
where python
# Should show: module_5\.venv\Scripts\python.exe
# NOT: C:\Python314\python.exe
```

### Check 2: Are packages installed?
```bash
pip list | findstr beautifulsoup4
# Should show: beautifulsoup4   4.12.3
```

### Check 3: Are scripts where they should be?
```bash
dir src\module_2_1\scrape.py
dir src\module_2_1\clean.py
dir src\load_data.py
# All should exist
```

---

## 🚀 Quick Fix

1. **Stop Flask** (Ctrl+C in terminal)
2. **Close the terminal window**
3. **Double-click** `START_FLASK_HERE.bat`
4. **Try "Pull Data" again**

That's it!
