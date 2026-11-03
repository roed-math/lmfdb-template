#!/usr/bin/env python
"""
Set up a new, empty database for the website (see docs/SETUP_POSTGRES.md):

- psycodict's metadata tables (meta_tables, meta_indexes, ...);
- the tables of the knowls and the user accounts (kwl_knowls, userdb.users, ...);
- access for the website's role to all of them;
- optionally, a first administrator.

Run it as the role owning the database, for example

    sage -python scripts/init_db.py --config-file owner.ini --admin yourname

Running it again does not change tables that exist already.
"""

import os
from getpass import getpass

from _common import parser, use_config

p = parser("Set up a new database for the website")
p.add_argument("--admin", metavar="USERNAME",
               help="create an administrator with this username (asks for the password)")
p.add_argument("--full-name", help="the administrator's full name")
p.add_argument("--read-only-web", action="store_true",
               help="let the website's role only read the knowls and users "
                    "(no logging in or editing, as on a public mirror)")
args = p.parse_args()
use_config(args)

from psycodict.database import PostgresDatabase  # noqa: E402
from lmfdb_utils.schema import add_user, create_tables, grant_website_access  # noqa: E402
from website.config import WEB_ROLE, configuration  # noqa: E402
from website.site import grant_policy  # noqa: E402

# create=True creates psycodict's metadata tables
db = PostgresDatabase(config=configuration(), grant_policy=grant_policy(), create=True)
create_tables(db)
if db._existing_roles([WEB_ROLE], missing="skip"):
    grant_website_access(db, WEB_ROLE, edit=not args.read_only_web)
else:
    print("There is no role %s yet (see docs/SETUP_POSTGRES.md); run this again once it exists" % WEB_ROLE)

if args.admin:
    # SITE_ADMIN_PASSWORD is for automated setups (such as tests); otherwise
    # the password is asked for
    password = os.environ.get("SITE_ADMIN_PASSWORD")
    if not password:
        password = getpass("Password for %s: " % args.admin)
        if password != getpass("Repeat the password: "):
            raise SystemExit("The passwords do not match")
    add_user(db, args.admin, password, full_name=args.full_name, admin=True, knowl_reviewer=True)
