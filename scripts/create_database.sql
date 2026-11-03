-- Create the database of the website and its two roles (see
-- docs/SETUP_POSTGRES.md).  Run it as a PostgreSQL superuser, choosing the
-- passwords:
--
--     psql -U postgres -v owner_password=... -v web_password=... -f scripts/create_database.sql
--
-- Without -v, the passwords below are used: fine on your own computer, not on
-- a server.  If you renamed the database or the roles in website/config.py,
-- rename them here too.

\if :{?owner_password}
\else
\set owner_password owner-password
\endif
\if :{?web_password}
\else
\set web_password web-password
\endif

-- Owns the tables: creates them and loads the data (scripts/*.py)
CREATE ROLE mysite_owner LOGIN PASSWORD :'owner_password';
-- Used by the website: reads the data, saves statistics, edits knowls
CREATE ROLE mysite_web LOGIN PASSWORD :'web_password';

CREATE DATABASE mysite OWNER mysite_owner ENCODING 'UTF8' TEMPLATE template0;
