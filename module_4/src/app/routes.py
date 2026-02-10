# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#
"""
routes.py — Module 3 Flask Route Handlers
-----------------------------------------
This module defines the HTTP routes for the Grad School Café dashboard.

Key responsibilities:
• Serve the main dashboard page.
• Trigger database queries when the user clicks “Update Analysis”.
• Format query results for display in HTML templates.
• Provide a clean separation between UI logic and SQL logic (queries.py).

This file connects user actions in the browser to the underlying database
analysis pipeline.
"""


# app/routes.py

import os
from flask import Blueprint, render_template, redirect, url_for, flash
import subprocess
from .queries import get_all_results, compute_scraper_diagnostics
import json
from pathlib import Path 
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, "..", "..")) 
TIMESTAMP_FILE = os.path.join(PROJECT_ROOT, "module_3", "last_pull.txt")
RUNTIME_FILE = os.path.join(PROJECT_ROOT, "module_3", "last_runtime.txt")

bp = Blueprint("main", __name__)

pull_running = False  # simple in-memory flag

def get_last_pull(): 
    if os.path.exists(TIMESTAMP_FILE): 
        return Path(TIMESTAMP_FILE).read_text(encoding="utf-8") 
    return None

def get_last_runtime(): 
    if os.path.exists(RUNTIME_FILE): 
        return Path(RUNTIME_FILE).read_text(encoding="utf-8") 
    return None

def load_scraped_records(): 
    path = Path(os.path.join(PROJECT_ROOT, "module_3", "module_2.1", "llm_extend_applicant_data.json"))

    if path.exists(): 
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    return []

@bp.route("/") 
def analysis(): 
    results = get_all_results() 

    # Load scraped JSON rows 
    records = load_scraped_records()

    # Then compute diagnostics using those rows
    scraper_diag = compute_scraper_diagnostics(records) 
    
    return render_template( 
        "analysis.html", 
        results=results, 
        scraper_diag=scraper_diag, 
        pull_running=pull_running, 
        last_data_pull=get_last_pull(),
        last_runtime=get_last_runtime() 
    )

@bp.route("/pull-data", methods=["POST"])
def pull_data():
    global pull_running, last_data_pull

    last_data_pull = "N/A" 
    runtime_str = "N/A"

    if pull_running:
        flash("A data pull is already running.")
        return redirect(url_for("main.analysis"))

    pull_running = True

    start_time = datetime.now()
    
    try:        
        # Run scraper 
        SCRAPER = os.path.join(PROJECT_ROOT, "module_3", "module_2.1", "scrape.py") 

        subprocess.run(["python", SCRAPER], check=True, cwd=PROJECT_ROOT) 
        
        last_data_pull = datetime.now().strftime("%b %d, %Y %I:%M %p") 
        flash("Scraper completed successfully.") 
        
        # Run cleaner 
        CLEANER = os.path.join(PROJECT_ROOT, "module_3", "module_2.1", "clean.py") 
        subprocess.run(["python", CLEANER], check=True, cwd=PROJECT_ROOT) 
        
        # Load cleaned data into PostgreSQL
        LOADER = os.path.join(PROJECT_ROOT, "module_3", "load_data.py") 
        subprocess.run(["python", LOADER, "--drop"], check=True, cwd=PROJECT_ROOT) 
        
        flash("Data pull complete. New entries added to the database.")

        end_time = datetime.now() 
        runtime_seconds = int((end_time - start_time).total_seconds()) 
        minutes, seconds = divmod(runtime_seconds, 60) 
        runtime_str = f"{minutes}m {seconds}s"

    except subprocess.CalledProcessError as e:
        flash(f"Subprocess error: {e}")
    except Exception as e:
        flash(f"Error during data pull: {e}")
        if hasattr(e, 'stdout'): 
            flash(f"STDOUT: {e.stdout}") 
        if hasattr(e, 'stderr'): 
            flash(f"STDERR: {e.stderr}")

    finally:
        pull_running = False

    with open(TIMESTAMP_FILE, "w", encoding="utf-8") as f: 
        f.write(str(last_data_pull))

    with open(RUNTIME_FILE, "w", encoding="utf-8") as f: 
        f.write(str(runtime_str))

    return redirect(url_for("main.analysis"))


@bp.route("/update-analysis", methods=["POST"])
def update_analysis():
    global pull_running

    if pull_running:
        flash("Cannot update analysis while data pull is running.")
        return redirect(url_for("main.analysis"))

    results = get_all_results()

    # Load scraped JSON rows
    records = load_scraped_records()

    # Compute diagnostics
    scraper_diag = compute_scraper_diagnostics(records) 

    flash("Analysis updated with the latest data.")
    return render_template(
        "analysis.html", 
        results=results, 
        scraper_diag=scraper_diag,
        pull_running=pull_running,
        last_data_pull=get_last_pull(),
        last_runtime=get_last_runtime() 
        )
