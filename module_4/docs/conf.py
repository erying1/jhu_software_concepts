import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Grad Café Analytics'
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
