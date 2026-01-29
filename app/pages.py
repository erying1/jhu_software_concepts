# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 1 Assignment: Personal Website
#
# app/pages.py
#

from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    return render_template("pages/home.html",active_page='home')

@bp.route("/contact")
def contact():
    return render_template("pages/contact.html", active_page='contact')

@bp.route("/projects")
def projects():
    return render_template("pages/projects.html", active_page='projects')




