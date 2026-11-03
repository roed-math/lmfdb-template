"""
An example section: the ways of writing n as a sum of two squares, for
n up to a bound (loaded by scripts/load_example.py).

Copy this directory to start a section of your own, and register its
blueprint in website/app.py.
"""

from flask import Blueprint

example_page = Blueprint("example", __name__, template_folder="templates")

from . import main  # noqa: E402  (adds the pages to example_page)

assert main
