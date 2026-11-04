"""
The configuration of the website: how to connect to the database, and the
secret key signing the cookies of logged in users.

Both are kept next to each other, at the root of the checkout by default:

- ``config.ini``, created with the default values the first time the website
  or a script runs (edit it to change them);
- ``secrets.ini`` (optional), whose values override ``config.ini``, for the
  password (see docs/SETUP_POSTGRES.md); another configuration file
  ``<name>.ini``, such as the owner's ``owner.ini``, has its own
  ``<name>-secrets.ini``;
- ``secret_key``, created the first time the website runs.

The ``SITE_CONFIG`` environment variable, or the ``--config-file`` option of
the scripts, gives another configuration file (for example one connecting as
the role that loads data).  None of these files are committed to git.
"""

import os
import secrets
import tempfile

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


def secrets_file(config_file_name):
    """
    The secrets file overriding the configuration file ``config_file_name``:
    ``secrets.ini`` next to ``config.ini``, and ``<name>-secrets.ini`` next to
    any other ``<name>.ini``, so that configurations for different roles do
    not share a password.
    """
    directory, filename = os.path.split(os.path.abspath(config_file_name))
    if filename == "config.ini":
        return os.path.join(directory, "secrets.ini")
    return os.path.join(directory, os.path.splitext(filename)[0] + "-secrets.ini")


def _configuration_from(config_file_name):
    return Configuration(defaults=dict(DEFAULTS, config_file=config_file_name,
                                       secrets_file=secrets_file(config_file_name)))


def configuration(config_file_name=None):
    """
    The psycodict configuration for connecting to the database, read from
    ``config_file_name`` (by default, see :func:`config_file`) and its secrets
    file (see :func:`secrets_file`).  The configuration file is created with
    the defaults if it does not exist.
    """
    global _configuration
    if config_file_name is not None:
        return _configuration_from(config_file_name)
    if _configuration is None:
        _configuration = _configuration_from(config_file())
    return _configuration


def secret_key():
    """
    The key signing the session cookies (which keep users logged in), kept in
    the file ``secret_key`` next to the configuration file.
    """
    path = os.path.join(os.path.dirname(config_file()), "secret_key")
    if not os.path.exists(path):
        # Several processes (the workers of a server) may start at once: each
        # writes a complete key to a file of its own, readable only by its
        # owner, and links it to secret_key, which only the first succeeds in
        # doing.  So secret_key never exists without its key, and all of them
        # use the first key.
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".secret_key.")
        try:
            with os.fdopen(fd, "w") as F:
                F.write(secrets.token_hex(32))
                F.flush()
                os.fsync(F.fileno())
            try:
                os.link(tmp, path)
            except FileExistsError:
                pass
        finally:
            os.unlink(tmp)
    with open(path) as F:
        key = F.read().strip()
    if not key:
        raise RuntimeError("The secret key in %s is empty: delete the file to make a new one" % path)
    return key
