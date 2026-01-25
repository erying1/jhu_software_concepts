# jhu_software_concepts
Modern Software Concepts JHU class EN.605.256 (82) - Spring 2026

=========================================================
Modern Concepts in Python: Spring 2026
Module 1 Assignment: Personal Website
Author: Eric Rying
=========================================================

PROJECT DESCRIPTION:
This is a Flask-based personal website developed as part of Module 1. 
The application utilizes Blueprint architecture to manage routes, 
Jinja2 template inheritance for layout consistency, and custom CSS 
[cite_start]for a responsive design[cite: 1].

DIRECTORY STRUCTURE:
module_1/
├── app/
│   ├── static/
│   │   ├── styles.css
│   │   └── Eric_Rying_bio_photo.png
│   ├── templates/
│   │   ├── base.html
│   │   ├── _navigation.html
│   │   └── pages/
│   │       ├── home.html
│   │       ├── contact.html
│   │       └── projects.html
│   ├── __init__.py
│   └── pages.py
├── run.py
├── requirements.txt
└── README.txt

PREREQUISITES:
- Python 3.10 or higher
- pip (Python package installer)

INSTALLATION & SETUP:
1. Navigate to the root directory (module_1).
2. (Optional but recommended) Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. Install the required dependencies using the requirements.txt file:
   pip install -r requirements.txt

HOW TO RUN THE APPLICATION:
1. Ensure you are in the root directory where 'run.py' is located.
2. Execute the following command in your terminal:
   python run.py
3. The server will start on http://0.0.0.0:8080.
4. Open your web browser and navigate to http://localhost:8080 to view the site.

NOTES:
- The navigation bar is located at the top right of each screen.
- The current page is highlighted in the navigation bar for easy tracking.
- The homepage features a bio section with text on the left and a profile image on the right.
