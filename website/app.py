"""
The Flask application.

lmfdb-utils provides the page layout, the style sheet, search results and
statistics pages, knowls (/knowledge) and user accounts (/users); this adds
the website's own pages and sections.  Its templates are in
website/templates, which take precedence over lmfdb-utils' (see
docs/CUSTOMIZING.md), and its static files in website/static.
"""

from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from lmfdb_utils.web import init_app

from .config import secret_key

app = Flask(__name__)
# Behind a web server such as nginx, use the address the browser requested
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = secret_key()

# The site was installed by website/__init__.py
init_app(app)


@app.context_processor
def site_context():
    # Shown in the footer of every page (see templates/homepage.html)
    return {"shortthanks": None}


##############################
#        Top-level pages     #
##############################

@app.route("/")
def index():
    return render_template("index.html", title="Example Database", bread=None)


@app.route("/about")
def about():
    return render_template("about.html", title="About", bread=[("About", " ")])


@app.route("/health")
def health():
    # for monitoring: checks that the database answers
    from psycodict import SQL
    from . import db
    db._execute(SQL("SELECT 1"))
    return "OK"


@app.errorhandler(404)
def not_found(error):
    app.logger.info("404 error for %s: %s", request.url, error.description)
    messages = error.description if isinstance(error.description, (list, tuple)) else (error.description,)
    return render_template("404.html", title="Page not found", messages=messages), 404


@app.errorhandler(500)
def server_error(error):
    app.logger.error("500 error for %s: %s", request.url, error)
    return render_template("500.html", title="Error"), 500


##############################
#          Sections          #
##############################

# Each section is a Flask blueprint in website/sections; add yours here.
from .sections.example import example_page  # noqa: E402

app.register_blueprint(example_page, url_prefix="/Example")
