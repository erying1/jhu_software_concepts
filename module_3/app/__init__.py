# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#
# /app/__init__.py
#

from flask import Flask
from datetime import datetime  # optional if you want timestamp filters later

def create_app():
    app = Flask(__name__)
    app.secret_key = "abc123" 

    # ------------------------- 
    # # Add missing Jinja filters 
    # # ------------------------- 
    @app.template_filter("na") 
    def na(value): 
        return value if value not in (None, "None") else "N/A"

    # -----------------------------
    # Jinja filter: format percentages
    # -----------------------------
    @app.template_filter("pct")
    def pct(value):
        if value is None:
            return "N/A"
        try:
            return f"{float(value):.2f}"
        except:
            return "N/A"

    # Register routes
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
