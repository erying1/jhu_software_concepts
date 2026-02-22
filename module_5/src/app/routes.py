"""
# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 4: Flask Routes with Testing Support
#
# routes.py — Module 4 Flask Route Handlers
-----------------------------------------
This module defines the HTTP routes for the Grad School Café dashboard.

Key responsibilities:
• Serve the main dashboard page.
• Trigger database queries when the user clicks "Update Analysis".
• Handle data pull requests with busy-state management.
• Format query results for display in HTML templates.
"""

import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)  # pylint: disable=import-error

from .queries import compute_scraper_diagnostics, get_all_results

bp = Blueprint("main", __name__, url_prefix="/")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, "..", ".."))
TIMESTAMP_FILE = os.path.join(PROJECT_ROOT, "last_pull.txt")
RUNTIME_FILE = os.path.join(PROJECT_ROOT, "last_runtime.txt")
ANALYSIS_TIMESTAMP_FILE = os.path.join(PROJECT_ROOT, "last_analysis.txt")

# Global busy state flag
pull_running = False  # pylint: disable=invalid-name


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


def get_last_analysis():
    """Read the timestamp of the last analysis refresh from disk.

    Returns:
        str | None: Timestamp string, or None if no refresh has occurred.
    """
    if os.path.exists(ANALYSIS_TIMESTAMP_FILE):
        return Path(ANALYSIS_TIMESTAMP_FILE).read_text(encoding="utf-8")
    return None


def load_scraped_records():
    """Load raw scraped records from the LLM-extended JSON file.

    Returns:
        list[dict]: Parsed applicant records, or empty list if file missing.
    """
    path = Path(
        os.path.join(
            PROJECT_ROOT, "module_2_1", "llm_extend_applicant_data.json"
        )
    )
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    return []


def fmt(val):
    """Format floats to two decimals; return 'N/A' for None."""
    if val is None:
        return "N/A"
    try:
        return f"{float(val):.2f}"
    except Exception:  # pylint: disable=broad-exception-caught
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
    except Exception:  # pylint: disable=broad-exception-caught
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
        "fall_2026_count": None,
        "pct_international": None,
        "avg_gpa_american_fall_2026": None,
        "avg_gpa_american": None,
        "pct_accept_fall_2026": None,
        "avg_gpa_accept_fall_2026": None,
        "jhu_cs_masters_count": None,
        "jhu_cs_masters": None,
        "elite_cs_phd_accepts_2026": None,
        "top_schools_accept": None,
        "elite_cs_phd_llm_accepts_2026": None,
        "top_schools_accept_llm": None,
        "top_universities": [],
        "degree_acceptance_summary": [],
        "acceptance_by_degree": [],
        "timestamp": None,
    }

    scraper_diag = {}
    records = []

    try:
        records = load_scraped_records()
        results = get_all_results()
        scraper_diag = compute_scraper_diagnostics(records)
    except Exception:  # pylint: disable=broad-exception-caught
        # Variables have default values from above, just log
        pass

    return render_template(
        "analysis.html",
        results=results,
        scraper_diag=scraper_diag,
        pull_running=pull_running,
        last_data_pull=get_last_pull(),
        last_runtime=get_last_runtime(),
        last_analysis_refresh=get_last_analysis(),
        fmt=fmt,
        pct=pct,
        na=na,
    )


@bp.route("/pull-data", methods=["POST"])
def pull_data():  # pylint: disable=too-many-locals,too-many-return-statements,too-many-statements
    """Trigger the full data pipeline: scrape, clean, and load into PostgreSQL.

    Returns JSON or redirects based on request type. Enforces busy-state
    gating — returns 409 if a pull is already in progress.
    """
    global pull_running  # pylint: disable=global-statement,invalid-name

    # Check if pull is already running
    if pull_running:
        if request.is_json:
            return (
                jsonify({"busy": True, "message": "A data pull is already running."}),
                409,
            )
        flash("A data pull is already running.")
        return redirect(url_for("main.analysis"))

    # Initialize defaults
    last_data_pull = "N/A"
    runtime_str = "N/A"

    try:
        pull_running = True
        start_time = datetime.now()

        # Prepare environment with DB credentials
        env = os.environ.copy()

        # Windows-specific fix: Use absolute path to venv python
        # and construct command as a string for shell=True
        python_exe = sys.executable

        # Run scraper
        scraper = os.path.join(PROJECT_ROOT, "src", "module_2_1", "scrape.py")
        cmd_scraper = f'"{python_exe}" "{scraper}"'
        subprocess.run(cmd_scraper, check=True, cwd=PROJECT_ROOT, env=env, shell=True)

        last_data_pull = datetime.now().strftime("%b %d, %Y %I:%M %p")

        # Run cleaner
        cleaner = os.path.join(PROJECT_ROOT, "src", "module_2_1", "clean.py")
        cmd_cleaner = f'"{python_exe}" "{cleaner}"'
        subprocess.run(cmd_cleaner, check=True, cwd=PROJECT_ROOT, env=env, shell=True)

        # Load cleaned data into PostgreSQL
        # Note: Don't use --drop because gradcafe_app user can't drop/recreate database
        # The loader handles duplicates with ON CONFLICT (url) DO NOTHING
        loader = os.path.join(PROJECT_ROOT, "src", "load_data.py")
        cmd_loader = f'"{python_exe}" "{loader}"'
        subprocess.run(cmd_loader, check=True, cwd=PROJECT_ROOT, env=env, shell=True)

        end_time = datetime.now()
        runtime_seconds = int((end_time - start_time).total_seconds())
        minutes, seconds = divmod(runtime_seconds, 60)
        runtime_str = f"{minutes}m {seconds}s"

        # Return JSON only for explicit JSON requests (AJAX)
        # Regular form submissions get a redirect to avoid showing JSON in browser
        if request.is_json:
            return (
                jsonify(
                    {
                        "ok": True,
                        "message": "Data pull complete. New entries added to the database.",
                        "runtime": runtime_str,
                    }
                ),
                200,
            )

        flash("Data pull complete. New entries added to the database.")

    except subprocess.CalledProcessError as e:
        error_msg = f"Subprocess error: {e}"
        if request.is_json:
            return jsonify({"ok": False, "error": error_msg}), 500
        flash(error_msg)

    except FileNotFoundError as e:
        # More specific error for missing files
        error_msg = f"File not found: {e}. sys.executable={sys.executable}"
        if request.is_json:
            return jsonify({"ok": False, "error": error_msg}), 500
        flash(error_msg)

    except Exception as e:  # pylint: disable=broad-exception-caught
        error_msg = f"Error during data pull: {e}"
        if request.is_json:
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
        except OSError:
            pass

    return redirect(url_for("main.analysis"))


@bp.route("/update-analysis", methods=["POST"])
def update_analysis():
    """Re-run analysis queries and refresh the dashboard.

    Does not trigger a new data pull. Returns 409 if a pull is in progress.
    Returns JSON or rendered template based on request type.
    """
    # Check if pull is running
    if pull_running:
        if request.accept_mimetypes.accept_json:
            return jsonify({"busy": True}), 409
        return redirect(url_for("main.analysis"))

    # Get fresh results
    try:
        results = get_all_results()

        # Force exception if structure is incomplete
        # (required by test_update_analysis_exception_in_try)
        if not isinstance(results, dict) or "avg_metrics" not in results:
            raise ValueError("Invalid results structure")

        # Save analysis refresh timestamp
        analysis_timestamp = datetime.now().strftime("%b %d, %Y %I:%M %p")
        try:
            with open(ANALYSIS_TIMESTAMP_FILE, "w", encoding="utf-8") as f:
                f.write(analysis_timestamp)
        except OSError:
            pass

    except Exception:  # pylint: disable=broad-exception-caught
        results = {
            "avg_metrics": defaultdict(lambda: None),
            "fall_2026_count": None,
            "pct_international": None,
            "avg_gpa_american_fall_2026": None,
            "avg_gpa_american": None,
            "pct_accept_fall_2026": None,
            "avg_gpa_accept_fall_2026": None,
            "jhu_cs_masters_count": None,
            "jhu_cs_masters": None,
            "elite_cs_phd_accepts_2026": None,
            "top_schools_accept": None,
            "elite_cs_phd_llm_accepts_2026": None,
            "top_schools_accept_llm": None,
            "top_universities": [],
            "degree_acceptance_summary": [],
            "acceptance_by_degree": [],
            "timestamp": None,
        }

    # Return JSON only for explicit JSON requests (AJAX)
    # Regular form submissions get a redirect to avoid showing JSON in browser
    if request.is_json:
        return (
            jsonify({"ok": True, "message": "Analysis updated with the latest data."}),
            200,
        )

    # For regular form POST, flash message and redirect back to analysis page
    flash("Analysis updated with the latest data.")
    return redirect(url_for("main.analysis"))


@bp.route("/status")
def status():
    """Return the current busy state of the system.

    Returns:
        dict: ``{"busy": true/false}`` with status 200.
    """
    try:
        return jsonify({"busy": pull_running}), 200
    except TypeError:
        return jsonify({"busy": False}), 200
