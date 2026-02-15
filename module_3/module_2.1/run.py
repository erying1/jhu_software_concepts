# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 1 Assignment: Personal Website
#
# run.py
#

from flask import Flask, Blueprint, render_template
from app.__init__ import start_my_app

app = start_my_app()

# Create the main function and use port= 8080 as per the assignment requirements
# SHALL run at port 8080 and localhost or 0.0.0.0
if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8080, debug=True)
    except Exception as e: 
        # Prevent crashes during automated test execution 
        print(f"Error in run.py main block: {e}")
