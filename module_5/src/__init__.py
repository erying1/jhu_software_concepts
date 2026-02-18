"""Expose the Flask application factory for the src package.
This module makes the ``create_app`` function available at the package level,
allowing external code to initialize the Flask application using
``from src import create_app``.
"""

# module_5/src/__init__.py

from .app import create_app

# src/__init__.py

__all__ = ["create_app"]
