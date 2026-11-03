"""
The tests run the website against a database set up as in
docs/SETUP_POSTGRES.md (scripts/init_db.py and scripts/load_example.py),
connecting with config.ini (or $SITE_CONFIG), like the website.

The tests that log in and edit knowls need an administrator: set
SITE_TEST_ADMIN and SITE_ADMIN_PASSWORD to the username and password given
to scripts/init_db.py --admin.  They create and delete a knowl test.<random>.
"""

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="session")
def app():
    from website.app import app
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin():
    username = os.environ.get("SITE_TEST_ADMIN")
    password = os.environ.get("SITE_ADMIN_PASSWORD")
    if not (username and password):
        pytest.skip("set SITE_TEST_ADMIN and SITE_ADMIN_PASSWORD to test logging in")
    return username, password
