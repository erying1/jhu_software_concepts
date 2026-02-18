"""
setup.py — Module 5 package configuration.

Why packaging matters:
    Making the project installable with pip install -e . ensures that Python
    resolves imports consistently regardless of where tests or scripts are run
    from. Without this, sys.path hacks or PYTHONPATH exports are needed to make
    `from src.app import create_app` work. An editable install pins the source
    directory into the environment so that local runs, pytest, and CI all see
    the same package layout — eliminating "it works on my machine" import errors.
    Tools like uv can also extract requirements from setup.py when syncing
    environments, making reproducible installs easier to automate.
"""

from setuptools import find_packages, setup

setup(
    name="module_5",
    version="0.1.0",
    description="Grad Café Analytics — Module 5",
    packages=find_packages(exclude=["tests*", ".venv*", "py3-sphinx*"]),
    python_requires=">=3.10",
    install_requires=[
        "flask",
        "beautifulsoup4==4.12.3",
        "psycopg2-binary",
        "anthropic",
        "psycopg",
        "psycopg-binary",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pylint",
            "pydeps",
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx-autobuild",
        ]
    },
)
