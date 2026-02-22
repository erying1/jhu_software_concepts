# Pull Data Button Fix Summary

## ✅ **Fixed Paths in routes.py**

### **Problem:**
The "Pull Data" button was trying to run scripts from old module directories (module_3 and module_4) instead of module_5.

### **Changes Made:**

#### 1. Scraper Path (Line 210)
**Before:**
```python
PROJECT_ROOT, "module_4", "src", "module_2.1", "scrape.py"
```
**After:**
```python
PROJECT_ROOT, "module_5", "src", "module_2_1", "scrape.py"
```

#### 2. Cleaner Path (Line 218)
**Before:**
```python
PROJECT_ROOT, "module_4", "src", "module_2.1", "scrape.py"  # Wrong file!
```
**After:**
```python
PROJECT_ROOT, "module_5", "src", "module_2_1", "clean.py"  # Correct file!
```

#### 3. Loader Path (Line 223)
**Before:**
```python
PROJECT_ROOT, "module_4", "src", "load_data.py"
```
**After:**
```python
PROJECT_ROOT, "module_5", "src", "load_data.py"
```

#### 4. Timestamp/Runtime Files (Lines 41-42)
**Before:**
```python
TIMESTAMP_FILE = os.path.join(PROJECT_ROOT, "module_3", "last_pull.txt")
RUNTIME_FILE = os.path.join(PROJECT_ROOT, "module_3", "last_runtime.txt")
```
**After:**
```python
TIMESTAMP_FILE = os.path.join(PROJECT_ROOT, "last_pull.txt")
RUNTIME_FILE = os.path.join(PROJECT_ROOT, "last_runtime.txt")
```

#### 5. Scraped Data Path (Line 78)
**Before:**
```python
PROJECT_ROOT, "module_3", "module_2.1", "llm_extend_applicant_data.json"
```
**After:**
```python
PROJECT_ROOT, "module_2_1", "llm_extend_applicant_data.json"
```

---

## 🎯 **What "Pull Data" Does Now**

When you click "Pull Data", it executes this pipeline:

```
1. SCRAPE → module_5/src/module_2_1/scrape.py
            ↓
            Fetches new Grad Café entries

2. CLEAN  → module_5/src/module_2_1/clean.py
            ↓
            Normalizes and cleans the data

3. LOAD   → module_5/src/load_data.py --drop
            ↓
            Loads into PostgreSQL database

4. SAVE   → last_pull.txt (timestamp)
            last_runtime.txt (duration)
```

---

## ✅ **Verified:**
- ✓ Scraper script exists: `src/module_2_1/scrape.py`
- ✓ Cleaner script exists: `src/module_2_1/clean.py`
- ✓ Loader script exists: `src/load_data.py`
- ✓ All paths now point to module_5 directory

---

## 🧪 **Testing:**

To test the "Pull Data" button:

1. Make sure Flask app is running with database credentials:
   ```bash
   run_flask.bat
   ```

2. Go to: http://localhost:8080

3. Click **"Pull Data"**

4. You should see:
   - Progress indicator (spinner)
   - Scraper runs → Clean runs → Load runs
   - Flash message: "Data pull complete. New entries added to the database."
   - Timestamp updated

---

## 📝 **Notes:**

- The `--drop` flag on the loader will drop/recreate the table
- Environment variables must be set (DB_HOST, DB_USER, DB_PASSWORD, etc.)
- Pull Data sets a `pull_running` flag to prevent concurrent runs
- Runtime is calculated and displayed after completion

All paths are now correct! The Pull Data button will work with module_5 scripts.
