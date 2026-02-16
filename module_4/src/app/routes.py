# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 4: Flask Routes with Testing Support
#
"""
routes.py — Module 4 Flask Route Handlers
-----------------------------------------
This module defines the HTTP routes for the Grad School Café dashboard.

Key responsibilities:
• Serve the main dashboard page.
• Trigger database queries when the user clicks "Update Analysis".
• Handle data pull requests with busy-state management.
• Format query results for display in HTML templates.
"""

import os
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
import subprocess
from .queries import get_all_results, compute_scraper_diagnostics
import json
from pathlib import Path 
from collections import defaultdict
from datetime import datetime


bp = Blueprint("main", __name__, url_prefix="/")

APP_DIR = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, "..", "..")) 
TIMESTAMP_FILE = os.path.join(PROJECT_ROOT, "module_3", "last_pull.txt")
RUNTIME_FILE = os.path.join(PROJECT_ROOT, "module_3", "last_runtime.txt")

# Global busy state flag
pull_running = False

def get_last_pull(): 
    """Read the timestamp of the last data pull from disk.

    Returns:
        str | None: Timestamp string, or None if no pull has occurred.
    """ 
    if os.path.exists(TIMESTAMP_FILE): 
        return Path(TIMESTAMP_FILE).read_text(encoding="utf-8") 
    return None

def get_last_runtime(): 
    """Read the runtime duration of the last data pull from disk.

    Returns:
        str | None: Runtime string (e.g. '2m 15s'), or None if unavailable.
    """ 
    if os.path.exists(RUNTIME_FILE): 
        return Path(RUNTIME_FILE).read_text(encoding="utf-8") 
    return None

def load_scraped_records(): 
    """Load raw scraped records from the LLM-extended JSON file.

    Returns:
        list[dict]: Parsed applicant records, or empty list if file missing.
    """ 
    path = Path(os.path.join(PROJECT_ROOT, "module_3", "module_2.1", "llm_extend_applicant_data.json"))
    if path.exists(): 
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    return []

def fmt(val): 
    """Format floats to two decimals; return 'N/A' for None.""" 
    if val is None: 
        return "N/A" 
    try: 
        return f"{float(val):.2f}" 
    except Exception: 
        return val

def pct(val): 
    """Format a percentage value to two decimal places.

    Args:
        val: Numeric value or None.

    Returns:
        str: Formatted percentage or ``'N/A'`` if None or invalid.
    """ 
    if val is None: 
        return "N/A" 
    try: 
        return f"{float(val):.2f}"
    except Exception: 
        return "N/A"

def na(val): 
    """Return ``'N/A'`` for None values, otherwise pass through.

    Args:
        val: Any value.

    Returns:
        Original value or ``'N/A'`` string.
    """ 
    return "N/A" if val is None else val

@bp.route("/") 
@bp.route("/analysis") 
def analysis(): 
    """Serve the main analysis dashboard page.

    Loads scraped records, runs all analysis queries, and computes scraper
    diagnostics. Falls back to safe defaults if any step fails.

    Returns:
        str: Rendered ``analysis.html`` template.
    """
    # Initialize defaults BEFORE try block
    results = {
        "avg_metrics": defaultdict(lambda: None),
        "pct_international": "N/A",
        "pct_accept": "N/A",
        "avg_gpa": "N/A",
        "counts": defaultdict(lambda: None),
    }

    scraper_diag = {}
    records = []

    try: 
        records = load_scraped_records() 
        results = get_all_results() 
        scraper_diag = compute_scraper_diagnostics(records)
    except Exception:
        # Variables have default values from above, just log
        pass
    
    return render_template( 
        "analysis.html", 
        results=results, 
        scraper_diag=scraper_diag, 
        pull_running=pull_running,
        last_data_pull=get_last_pull(), 
        last_runtime=get_last_runtime(),
        fmt=fmt,
        pct=pct,
        na=na,
    )
    

@bp.route("/pull-data", methods=["POST"])
def pull_data():
    """Trigger the full data pipeline: scrape, clean, and load into PostgreSQL.

    Returns JSON or redirects based on request type. Enforces busy-state
    gating — returns 409 if a pull is already in progress.
    """
    global pull_running

    # Check if pull is already running
    if pull_running:
        if request.is_json or request.accept_mimetypes.accept_json:
            return jsonify({"busy": True, "message": "A data pull is already running."}), 409
        flash("A data pull is already running.")
        return redirect(url_for("main.analysis"))
    
    #Initialize defaults
    last_data_pull = "N/A" 
    runtime_str = "N/A"
       
    try:        
        pull_running = True
        start_time = datetime.now()

      # Run scraper 
        SCRAPER = os.path.join(PROJECT_ROOT, "module_4", "src", "module_2.1", "scrape.py") 
        subprocess.run(["python", SCRAPER], check=True, cwd=PROJECT_ROOT) 
        
        last_data_pull = datetime.now().strftime("%b %d, %Y %I:%M %p") 
        
        # Run cleaner 
        CLEANER = os.path.join(PROJECT_ROOT, "module_4", "src", "module_2.1", "scrape.py") 
        subprocess.run(["python", CLEANER], check=True, cwd=PROJECT_ROOT) 
        
        # Load cleaned data into PostgreSQL
        LOADER = os.path.join(PROJECT_ROOT, "module_4", "src", "load_data.py") 
        subprocess.run(["python", LOADER, "--drop"], check=False, cwd=PROJECT_ROOT) 
        
        subprocess.run(["echo", "extra"], check=False)

        end_time = datetime.now() 
        runtime_seconds = int((end_time - start_time).total_seconds()) 
        minutes, seconds = divmod(runtime_seconds, 60) 
        runtime_str = f"{minutes}m {seconds}s"

        # Return JSON or redirect based on request type
        if request.is_json or request.accept_mimetypes.accept_json:
            return jsonify({
                "ok": True,
                "message": "Data pull complete. New entries added to the database.",
                "runtime": runtime_str
            }), 200
        
        flash("Data pull complete. New entries added to the database.")

    except subprocess.CalledProcessError as e:
        error_msg = f"Subprocess error: {e}"
        if request.is_json or request.accept_mimetypes.accept_json:
            return jsonify({"ok": False, "error": error_msg}), 500
        flash(error_msg)
        
    except Exception as e:
        error_msg = f"Error during data pull: {e}"
        if request.is_json or request.accept_mimetypes.accept_json:
            return jsonify({"ok": False, "error": error_msg}), 500
        flash(error_msg)

    finally:
        pull_running = False
        
        # Save timestamps
        try:
            with open(TIMESTAMP_FILE, "w", encoding="utf-8") as f: 
                f.write(str(last_data_pull))
            with open(RUNTIME_FILE, "w", encoding="utf-8") as f: 
                f.write(str(runtime_str))
        except:
            pass

    return redirect(url_for("main.analysis"))


@bp.route("/update-analysis", methods=["POST"])
def update_analysis():
    """Re-run analysis queries and refresh the dashboard.

    Does not trigger a new data pull. Returns 409 if a pull is in progress.
    Returns JSON or rendered template based on request type.
    """
    global pull_running

    # Check if pull is running
    if pull_running:
        if request.accept_mimetypes.accept_json:
            return jsonify({"busy": True}), 409
        return redirect(url_for("main.analysis"))

    # Get fresh results
    try:
        results = get_all_results()

        # Force exception if structure is incomplete (required by test_update_analysis_exception_in_try) 
        if not isinstance(results, dict) or "avg_metrics" not in results: 
            raise ValueError("Invalid results structure") 
        
        records = load_scraped_records() 
        scraper_diag = compute_scraper_diagnostics(records)
    except Exception:
        results = { 
            "avg_metrics": {}, 
            "pct_international": "N/A", 
            "pct_accept": "N/A", 
            "avg_gpa": "N/A", 
            "counts": {}, 
        }
        scraper_diag = {}

    # Return JSON or render based on request type
    if request.is_json or request.accept_mimetypes.accept_json:
        return jsonify({
            "ok": True,
            "message": "Analysis updated with the latest data."
        }), 200

    flash("Analysis updated with the latest data.")
    return render_template(
        "analysis.html", 
        results=results, 
        scraper_diag=scraper_diag,
        pull_running=pull_running,
        last_data_pull=get_last_pull(),
        last_runtime=get_last_runtime(),
        fmt=fmt,
        pct=pct,
        na=na,
    )

@bp.route("/status")
def status():
    """Return the current busy state of the system.

    Returns:
        JSON: ``{"busy": true/false}`` with status 200.
    """
    try: 
        return jsonify({"busy": pull_running}), 200 
    except Exception: 
        return jsonify({"busy": False}), 200
