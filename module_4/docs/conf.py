import os
import sys

# Directory containing this conf.py file 
DOCS_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Project root (one level up from docs/) 
PROJECT_ROOT = os.path.abspath(os.path.join(DOCS_DIR, "..")) 

# Add project root so 'src' is importable as a package
sys.path.insert(0, PROJECT_ROOT)

project = 'Grad Cafe Analytics'
author = 'Eric Rying'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary', 
]
autosummary_generate = True

# Mock imports that aren't available in the Sphinx build environment
autodoc_mock_imports = [
    'psycopg',
    'flask',
    'anthropic',
    'bs4',
    'requests',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
