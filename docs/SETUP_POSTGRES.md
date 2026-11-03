# Setting up PostgreSQL

The website keeps everything in one PostgreSQL database: its data, the knowls
and the user accounts.  Two roles (PostgreSQL users) use it:

| role           | used by                                      | can                                                            |
|----------------|----------------------------------------------|----------------------------------------------------------------|
| `mysite_owner` | the scripts that create tables and load data | everything: it owns the database and its tables                |
| `mysite_web`   | the website                                  | read the data, save statistics, edit knowls, log users in      |

Keeping them separate means that a bug in the website cannot change or delete
your data.  The names are set in `website/config.py` (`DATABASE_NAME`,
`OWNER_ROLE`, `WEB_ROLE`) and `scripts/create_database.sql`; change them
there when you start your own website, before creating the database.

PostgreSQL 14 or later is needed.

## 1. Install PostgreSQL

Choose one:

- **Docker** (simplest for development): `docker compose up -d` in the
  checkout starts PostgreSQL 16, listening on `localhost:5432`, and creates
  the database and roles of step 2 with the default passwords in
  `scripts/create_database.sql`.  The data lives in a Docker volume, so it
  survives restarts (`docker compose down -v` deletes it).  Skip step 2.
- **Ubuntu/Debian**: `sudo apt install postgresql`.  Run the commands of
  step 2 as the `postgres` user: `sudo -u postgres psql ...`.
- **macOS**: [Postgres.app](https://postgresapp.com), or
  `brew install postgresql@16 && brew services start postgresql@16`.  Your
  macOS user is a superuser: run `psql -d postgres ...`.
- **A server run by someone else** (your department, a cloud provider): ask
  for a database and the two roles, or for a role allowed to create them.

## 2. Create the database and its roles

As a PostgreSQL superuser, choosing two passwords:

```
psql -U postgres -v owner_password=CHOOSE-ONE -v web_password=CHOOSE-ANOTHER -f scripts/create_database.sql
```

(Without the `-v` options the passwords are `owner-password` and
`web-password`: fine on your own computer, not on a server.)

## 3. Tell the website how to connect

The website connects with `config.ini`, at the root of the checkout, which is
created with the defaults of `website/config.py` the first time anything runs.
Create it now instead, with the website's role:

```ini
[postgresql]
host = localhost
port = 5432
user = mysite_web
password = web-password
dbname = mysite
```

The scripts that change the database connect as the owner, with a second file
given by `--config-file`, say `owner.ini`:

```ini
[postgresql]
host = localhost
port = 5432
user = mysite_owner
password = owner-password
dbname = mysite
```

Neither file is committed (see `.gitignore`).  To keep the password out of a
file you share, put a `[postgresql]` section with just `password = ...` in
`secrets.ini` next to the configuration file: its values override it.  A
different configuration file for the website can be given with the
`SITE_CONFIG` environment variable.

If PostgreSQL runs on the same machine and you prefer to connect through its
Unix socket (no password), set `host` to the socket directory, such as
`/var/run/postgresql`, and give the roles the same names as Unix users that
run the website and scripts.

## 4. Create the tables

```
sage -python scripts/init_db.py --config-file owner.ini --admin yourname --full-name "Your Name"
```

This creates

- psycodict's metadata tables (`meta_tables`, `meta_indexes`, ... and their
  `_hist` versions), which describe the tables of the website's data;
- the knowls (`kwl_knowls`, with every version of every knowl, and
  `kwl_locks`), and the user accounts (`userdb.users` and `userdb.tokens`);

grants the website's role access to them, and creates an administrator
`yourname` (asking for a password), who can invite other users from
`/users/register/new` and review knowls.  It can be run again: existing tables
are left alone.

## 5. Load data

The example section's data and knowls:

```
sage -python scripts/load_example.py --config-file owner.ini
```

`scripts/load_example.py` is the model for loading your own data with
psycodict:

1. `db.create_table(name, columns, label_col=..., sort=...)` creates a table.
   Table names are lowercase letters, digits and underscores; by convention
   they start with the name of their section (`example_sums`).  The roles in
   `grant_policy()` (in `website/site.py`) get access to new tables
   automatically.
2. `db.<table>.insert_many(rows)` adds rows given as dictionaries.  For large
   data, write a file and use `copy_from` or `reload` instead (see the
   [psycodict documentation](https://psycodict.readthedocs.io/en/latest/DataManagement.html)).
3. `db.<table>.create_index([...])` for the columns searched most.
4. The statistics shown on statistics pages are stored in the tables
   `<table>_counts` and `<table>_stats`.  The website's role can add counts
   for new searches, but computing whole distributions is done when loading
   the data: `MyStats().setup()` for a `StatsDisplay` subclass (see the
   example), then `db.<table>.stats.refresh_stats()` after the data changes.

Knowls are normally written on the website (log in, then click a missing
knowl, or go to `/knowledge`).  `knowldb.yaml_export` and
`knowldb.yaml_import` copy them to and from a YAML file, as
`knowls/example.yaml`.

## 6. Check

```
sage -python start-site.py --debug
```

and open http://127.0.0.1:37778.  `sage -python -m pytest tests` runs the
tests (see the README).

## Backups

`pg_dump -Fc -U mysite_owner mysite > mysite.dump` saves everything (data,
knowls, users); `pg_restore -d mysite mysite.dump` restores it into an empty
database.  Run it regularly on a server, for example from cron, and keep the
dumps somewhere else.

## A public read-only copy

To let anyone run queries (as the LMFDB does with devmirror.lmfdb.xyz), or
to run a public website that only shows knowls while editing happens on a
separate beta website, create a role that can only read:

```sql
CREATE ROLE mysite_reader LOGIN PASSWORD '...';
-- connected to the database mysite, as mysite_owner:
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mysite_reader;
-- and the tables created later
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mysite_reader;
```

and, connected as the owner, `grant_website_access(db, "mysite_reader",
edit=False)` from `lmfdb_utils.schema` (or `scripts/init_db.py
--read-only-web` when the website's role should be read-only).  With such a
role the website shows knowls, but nobody can log in.

## Troubleshooting

- *password authentication failed* or *Peer authentication failed*: check the
  role and password in `config.ini`; with a packaged PostgreSQL, connections
  to `localhost` need a password while socket connections use your Unix
  user name (see `pg_hba.conf`).
- *permission denied for table ...* on the website: the table was created
  before the website's role existed, or by hand.  Connected as the owner:
  `GRANT SELECT ON ALL TABLES IN SCHEMA public TO mysite_web;`.
- *AttributeError: ... has no attribute 'example_sums'*: the example data has
  not been loaded (step 5).
- *This database uses metadata format 0*: the database was created by an
  older psycodict; run `db.upgrade_metadata()` as the owner.
