# Making the website yours

Everything you are expected to change is in `website/`, `knowls/`,
`scripts/` (your loading scripts) and `tests/`.  Keeping your changes there,
and changing the template's other files only when needed, makes it easy to
merge later improvements to the template (see [UPDATING.md](UPDATING.md)).

## Name, logo, home page

- `website/site.py`: the name of the website (in page titles and in
  "downloaded from the ..."), the prefix of downloaded files, the description
  for search engines, the logo, where users report problems (`feedback_url`),
  and the address of your repository (`source_url_base`, used to link to code
  from knowls).  `lmfdb_utils/site.py` documents every attribute.
- `website/static/images/logo.svg` and `favicon.svg`: replace them (any
  format; update `logo` in `site.py` and the link in `templates/base.html`).
- `website/templates/index.html`: the home page; `about.html`: the about page.
- `website/config.py`: the names of the database and its roles (change these
  before creating the database, see [SETUP_POSTGRES.md](SETUP_POSTGRES.md)).

## Colors and style

The style sheet `/style.css` comes from lmfdb-utils and takes its colors from
a color scheme: `SiteColors` in `website/colors.py`.  Its main colors are

| attribute      | colors                                                  |
|----------------|---------------------------------------------------------|
| `col_main_d`   | header and footer background (in some layouts)          |
| `col_main_dl`  | header and footer text                                  |
| `col_main`     | headings, and the default for most text colors          |
| `col_main_2`   | links when hovered                                      |
| `col_main_l`   | tabs and buttons                                        |
| `col_main_lg`  | borders and shadows of boxes                            |
| `col_main_ld`  | background of boxes (properties, search forms)          |
| `col_main_ll`  | light backgrounds (table rows, notices)                 |
| `col_link`     | links                                                   |
| `col_a_knowl`  | links that open knowls                                  |
| `knowl_hyper_text`, `knowl_shadow`, `knowl_border`, `knowl_background` | open knowls |

The other colors default to these; `ColorScheme.colors` in
`lmfdb_utils/color.py` lists them all, and the LMFDB's color schemes defined
there are examples.  To try another scheme, add `?color=<code>` to any
address (for example `?color=15`); logged in users can choose one on
`/users/myself`.  `default_color` in `website/site.py` chooses the scheme
used otherwise, and `color_schemes()` which ones are offered.

For changes beyond colors (fonts, sizes, layout), add rules to
`website/static/site.css`, which is loaded after `/style.css`.

## The layout of pages

Every page extends `homepage.html`, which fills in the blocks of
`lmfdb_utils/layout.html` from lmfdb-utils:

- `logo`: the logo in the header (by default the image `site.logo`);
- `undertopright`: links in the top right corner, each followed by `&middot;`;
- `footer`: the footer;
- `sidebar`, `content`, `body`: the sidebar, the page itself, everything.

and `base.html`, which fills in the blocks of `lmfdb_utils/base.html` (the
`<head>`):

- `head_early`: scripts needed early, such as a CAPTCHA;
- `head_late`: style sheets, the favicon, analytics;
- `katex_macros`: TeX macros for formulas (`{{ super() }}` keeps the LMFDB's).

Both are in `website/templates`.  Any other template of lmfdb-utils (for
example `search_results.html`, or `knowl-show.html` from its knowledge pages)
can be replaced the same way, by a file with the same name in
`website/templates`, and any of its static files by a file with the same name
in `website/static`.  Prefer filling in blocks to replacing whole templates:
a replaced template no longer receives improvements from lmfdb-utils.

Pages pass these variables to the layout (see the example section):

- `title`, and `bread` (breadcrumbs: a list of pairs (name, address));
- `properties`: pairs (name, value) shown in the box on the right;
- `friends` (related objects), `downloads`, `learnmore`: pairs (text,
  address) shown in boxes on the right;
- `credit`: who computed the data, shown in the footer;
- `KNOWL_ID`: shows the knowls `<KNOWL_ID>.top` and `<KNOWL_ID>.bottom` at the
  top and bottom of the page, so editors can annotate any object (link them
  back with `knowl_annotation_urls` in `website/site.py`).

## The sidebar

`website/sidebar.yaml` lists the sections of the sidebar and their links,
given by Flask endpoints (`url_for`): `index`, `about`, `knowledge.index`, or
`<blueprint>.<function>` for the pages of a section.  See
`lmfdb_utils/sidebar.py` for the options.

## Adding a section

A section is a table of objects with its pages, in a Flask blueprint.  To add
one, copy `website/sections/example` to `website/sections/<yours>` and:

1. write a script loading its data, following `scripts/load_example.py`
   (and [SETUP_POSTGRES.md](SETUP_POSTGRES.md), step 5);
2. in `__init__.py`, rename the blueprint (`Blueprint("<yours>", ...)`);
3. in `main.py`, adapt
   - the search form (`ExampleSearchArray`: one box per searchable column,
     `browse_array` for the main page, `refine_array` for the results page),
   - the search function (`example_search`: one `parse_*` call per box,
     turning what users type into a psycodict query; `lmfdb_utils.search_parsing`
     has parsers for integers, ranges, lists, rationals, ...),
   - the columns of the results (`SearchColumns`, see
     `lmfdb_utils.search_columns`),
   - the page of each object (`by_label`, `templates/<yours>-show.html`),
   - downloads (`Downloader`), statistics (`StatsDisplay`);
4. register the blueprint in `website/app.py`, add it to
   `website/sidebar.yaml` and `templates/index.html`;
5. write knowls for its terms (on the website, or in `knowls/<yours>.yaml`);
6. add its pages to `tests/test_site.py`.

The LMFDB's sections (in `lmfdb/` of the
[LMFDB repository](https://github.com/LMFDB/lmfdb)) are larger examples of
everything lmfdb-utils can do.

## Knowls

Knowls are written in Markdown with TeX (`$...$`), and can include other
knowls with `{{ KNOWL('id', 'text') }}`, cite references with
`\cite{arxiv:1809.10195}`, `\cite{mr:...}`, `\cite{doi:...}`,
`\cite{wikipedia:...}`, ..., and link to definitions elsewhere.  In
templates, `{{ KNOWL('id', 'text') }}` shows a term opening the knowl, and
`{{ KNOWL_INC('id') }}` includes its content.  Logged in users create a
missing knowl by clicking it, and edit any knowl from `/knowledge`;
reviewers mark them reviewed.  On a site that is not in beta (not in debug
mode), the last reviewed version of a knowl is shown.

## Users

Administrators create registration links at `/users/register/new` (ten at a
time) and send them to new editors; a link creates one account.  To make a
user an administrator or a reviewer, as the owner of the database:

```sql
UPDATE userdb.users SET admin = true, knowl_reviewer = true WHERE username = '...';
```
