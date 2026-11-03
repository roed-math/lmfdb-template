"""
The configuration of the website: how to connect to the database, and the
secret key signing the cookies of logged in users.

Both are kept next to each other, at the root of the checkout by default:

- ``config.ini``, created with the default values the first time the website
  or a script runs (edit it to change them);
- ``secrets.ini`` (optional), whose values override ``config.ini``, for the
  password (see docs/SETUP_POSTGRES.md);
- ``secret_key``, created the first time the website runs.

The ``SITE_CONFIG`` environment variable, or the ``--config-file`` option of
the scripts, gives another configuration file (for example one connecting as
the role that loads data).  None of these files are committed to git.
"""

import os
import secrets

from psycodict.config import Configuration

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: The defaults written to a new config.ini.  Change DATABASE_NAME and the
#: role names when you start your own website (see docs/SETUP_POSTGRES.md).
DATABASE_NAME = "mysite"
WEB_ROLE = "mysite_web"
OWNER_ROLE = "mysite_owner"

DEFAULTS = {
    "postgresql_host": "localhost",
    "postgresql_port": 5432,
    "postgresql_user": WEB_ROLE,
    "postgresql_password": "",
    "postgresql_dbname": DATABASE_NAME,
    # The website logs searches slower than this (in seconds) to
    # logs/slow_queries.log
    "logging_slowcutoff": 1.0,
}

_configuration = None


def config_file():
    return os.environ.get("SITE_CONFIG") or os.path.join(ROOT, "config.ini")


def configuration(config_file_name=None):
    """
    The psycodict configuration for connecting to the database, read from
    ``config_file_name`` (by default, see :func:`config_file`).  The file is
    created with the defaults if it does not exist.
    """
    global _configuration
    if config_file_name is not None:
        return Configuration(defaults=dict(DEFAULTS, config_file=config_file_name))
    if _configuration is None:
        _configuration = Configuration(defaults=dict(DEFAULTS, config_file=config_file()))
    return _configuration


def secret_key():
    """
    The key signing the session cookies (which keep users logged in), kept in
    the file ``secret_key`` next to the configuration file.
    """
    path = os.path.join(os.path.dirname(config_file()), "secret_key")
    if not os.path.exists(path):
        # created readable only by its owner; if another process creates it
        # first, use that one
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w") as F:
                F.write(secrets.token_hex(32))
    with open(path) as F:
        return F.read().strip()
