# LMFDB website template

A starting point for a mathematical database website in the style of the
[LMFDB](https://www.lmfdb.org): searchable tables of mathematical objects
stored in PostgreSQL, a page for each object, downloads to Sage, Magma, Pari
and other systems, statistics pages, and *knowls*, the definitions that pop up
when a term is clicked, which logged in users edit on the website.

The website itself is small: almost everything comes from
[lmfdb-utils](https://github.com/LMFDB/lmfdb/tree/main/packages/lmfdb-utils),
a package built from the LMFDB's own code and shared with it, so improvements
to the LMFDB reach your website when you update the package.

It comes with an example section, the ways of writing $n$ as a sum of two
squares, to copy when writing your own sections.

## Starting your own website

Use git rather than GitHub's "Use this template" button, so that you can
later merge improvements to the template (see [docs/UPDATING.md](docs/UPDATING.md)):

```
git clone https://github.com/LMFDB/lmfdb-template.git mysite
cd mysite
git remote rename origin template
# create an empty repository for your website on GitHub, then
git remote add origin https://github.com/<you>/<your-repository>.git
git push -u origin main
```

Then:

1. **Install [SageMath](https://doc.sagemath.org/html/en/installation/)**
   (lmfdb-utils needs it), and the website's dependencies into Sage's Python:
   `sage -pip install -r requirements.txt`.  (Or create a conda environment
   with Sage from `environment.yml`.)
2. **Set up PostgreSQL** and the website's database:
   [docs/SETUP_POSTGRES.md](docs/SETUP_POSTGRES.md).  With Docker, this is
   `docker compose up -d` followed by two scripts.
3. **Run the website**: `sage -python start-site.py --debug`, and open
   http://127.0.0.1:37778.
4. **Make it yours**: name, logo, colors, home page, sidebar, and your own
   sections: [docs/CUSTOMIZING.md](docs/CUSTOMIZING.md).
5. **Put it online**: [docs/DEPLOYING.md](docs/DEPLOYING.md).

## What is where

```
website/
  site.py            the name, logo, sidebar, colors... of the website (start here)
  colors.py          its color scheme
  config.py          the database connection (config.ini) and role names
  app.py             the Flask application: top-level pages and sections
  sidebar.yaml       the sidebar menu
  templates/         page templates: homepage.html (header and footer), base.html,
                     index.html (the home page), about.html, error pages
  static/            site.css, logo and other files served at /static/
  sections/example/  the example section: search, object pages, downloads, statistics
knowls/example.yaml  the knowls of the example section
scripts/
  create_database.sql  creates the database and its roles
  init_db.py           creates the tables of knowls and users, and an administrator
  load_example.py      loads the example data: a model for loading yours
tests/               tests of the pages, run by .github/workflows/tests.yml
docs/                setting up PostgreSQL, customizing, updating, deploying
start-site.py        runs the development server
```

Pages, search forms, result tables, statistics, the knowledge database
(`/knowledge`) and user accounts (`/users`) come from lmfdb-utils; its
[README](https://github.com/LMFDB/lmfdb/tree/main/packages/lmfdb-utils) lists
what it provides.  The database is accessed with
[psycodict](https://psycodict.readthedocs.io).

## Tests

With the database set up and the website's `config.ini` in place:

```
sage -python -m pytest tests
```

The tests that log in and edit a knowl run when `SITE_TEST_ADMIN` and
`SITE_ADMIN_PASSWORD` give an administrator (see `tests/conftest.py`).
GitHub Actions runs everything on each push, with a fresh database.

## License

GPL version 2 or later, like the LMFDB (see [LICENSE](LICENSE)).
