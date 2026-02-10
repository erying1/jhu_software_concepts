# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#

"""
run.py — Module 3 Flask Application Entrypoint
----------------------------------------------
This script launches the Flask web application that powers the interactive
Grad School Café analysis dashboard.

Key responsibilities:
• Initialize the Flask app and register routes.
• Serve the main dashboard page and the “Update Analysis” endpoint.
• Execute SQL queries (via queries.py) to compute statistics such as:
  – applicant counts
  – acceptance rates
  – GPA/GRE averages
  – Fall 2026 metrics
  – top universities and degree‑level acceptance rates
• Render results into HTML templates for user interaction.

This file is the user‑facing interface for the entire Module 2 → Module 3 pipeline.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
