"""queries.py — Flask-facing wrappers around SQL query and diagnostic logic."""

# src/app/queries.py

from datetime import datetime

import src.query_data as qd


def get_all_results():
    """
    Thin wrapper used by the Flask routes.
    Delegates all SQL logic to query_data.get_all_analysis().
    """
    results = qd.get_all_analysis()
    results["timestamp"] = datetime.now().strftime("%b %d, %Y %I:%M %p")
    return results


def compute_scraper_diagnostics(records):
    """Compute field-presence and field-absence counts for scraped records.

    Args:
        records (list[dict]): Raw applicant records from the JSON data file.

    Returns:
        dict: Counts of present and missing values for each tracked field.
    """
    total = len(records)

    def count(field):
        return sum(1 for r in records if r.get(field) not in (None, "", "null"))

    diagnostics = {
        "Total scraped rows": total,
        "Comments present": count("comments"),
        "Term present": count("term"),
        "Citizenship present": count("us_or_international"),
        "GPA present": count("gpa"),
        "GRE Total present": count("gre_total_score"),
        "GRE Verbal present": count("gre_verbal_score"),
        "GRE AW present": count("gre_aw_score"),
    }

    diagnostics.update(
        {
            "Comments missing": total - diagnostics["Comments present"],
            "Term missing": total - diagnostics["Term present"],
            "Citizenship missing": total - diagnostics["Citizenship present"],
            "GPA missing": total - diagnostics["GPA present"],
            "GRE Total missing": total - diagnostics["GRE Total present"],
            "GRE Verbal missing": total - diagnostics["GRE Verbal present"],
            "GRE AW missing": total - diagnostics["GRE AW present"],
        }
    )

    return diagnostics
