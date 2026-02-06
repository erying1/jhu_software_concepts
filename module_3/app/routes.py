# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#
# routes.py

# Overview of routes.py:
#
# This code handles: 
# 1) Rendering the analysis page
# 2) Running the scraper (via subprocess)
# 3) Running load_data.py
# 4) Refreshing the analysis
#
# Input file: TBD
# Output file: TBD

# app/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
import subprocess
from .queries import get_all_results

bp = Blueprint("main", __name__)

pull_running = False  # simple in-memory flag

@bp.route("/")
def analysis():
    results = get_all_results()
    return render_template("analysis.html", results=results, pull_running=pull_running)

@bp.route("/pull-data", methods=["POST"])
def pull_data():
    global pull_running

    if pull_running:
        flash("A data pull is already running.")
        return redirect(url_for("main.analysis"))

    pull_running = True
    try:
        # Run scraper
        subprocess.run(
            ["python", "module_2/scrape.py"],
            cwd="..",
            check=True
        )

        # Run cleaner
        subprocess.run(
            ["python", "module_2/clean.py"],
            cwd="..",
            check=True
        )

        # Load cleaned data into PostgreSQL
        subprocess.run(
            ["python", "load_data.py"],
            cwd="..",
            check=True
        )

        flash("Data pull complete. New entries added to the database.")

    except Exception as e:
        flash(f"Error during data pull: {e}")

    finally:
        pull_running = False

    return redirect(url_for("main.analysis"))


@bp.route("/update-analysis", methods=["POST"])
def update_analysis():
    global pull_running

    if pull_running:
        flash("Cannot update analysis while data pull is running.")
        return redirect(url_for("main.analysis"))

    # Re-run all SQL queries
    results = get_all_results()

    flash("Analysis updated with the latest data.")
    return render_template("analysis.html", results=results, pull_running=pull_running)
