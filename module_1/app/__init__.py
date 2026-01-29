# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 1 Assignment: Personal Website
#
# /app/__init__.py
#

# Import the flask module to help create the website as per the assignment requirements
# SHALL use Flask as your web framework

from flask import Flask

from app import pages

def start_my_app():
    app = Flask(__name__)
    app.register_blueprint(pages.bp)
    return app
