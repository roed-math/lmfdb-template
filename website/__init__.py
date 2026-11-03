"""
The website.

``from website import db`` gives the database (a psycodict
``PostgresDatabase``), which connects the first time it is used, with the
configuration in config.ini (see website/config.py).  ``sage -python
start-site.py`` runs the website (see README.md).

Importing this package describes the website to lmfdb-utils (see
website/site.py); the Flask application is in website/app.py.
"""

from lmfdb_utils.lazy import LazyObject
from lmfdb_utils.site import set_current_site

from .site import WebSite

set_current_site(WebSite())


def _make_database():
    from psycodict.database import PostgresDatabase
    from .config import configuration
    from .site import grant_policy
    return PostgresDatabase(config=configuration(), grant_policy=grant_policy())


db = LazyObject(_make_database, "The database (connected when first used)")

__all__ = ["db"]
