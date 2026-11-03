"""
How the website describes itself to lmfdb-utils: its name, logo, sidebar,
colors, database, and where its code lives (see lmfdb_utils/site.py for all
the attributes that can be set).

This is the first file to change when starting your own website.
"""

import os

from lmfdb_utils.site import Site

from .config import ROOT, WEB_ROLE

HERE = os.path.dirname(os.path.abspath(__file__))


class WebSite(Site):
    # The name of the website, in the titles of pages and in phrases like
    # "downloaded from the <name>"
    name = "Example Database"

    # The beginning of the names of downloaded files
    download_prefix = "example"

    # Shown by search engines
    meta_description = "An example of a website built from the LMFDB website template."

    # The logo in the header, in website/static (None to show the name)
    logo = "images/logo.svg"

    # The sections and pages listed in the sidebar
    sidebar_file = os.path.join(HERE, "sidebar.yaml")

    # Where users report problems: an address, such as a GitHub issues page
    feedback_url = None

    # Where the code is: the checkout (searched for references to knowls) and
    # its address online, for linking to files, for example
    # "https://github.com/<owner>/<repository>/blob/main/"
    source_root = ROOT
    source_url_base = None

    # Annotation knowls ("<label>.top" and "<label>.bottom") show text at the
    # top and bottom of the page of an object; this says which page, for each
    # kind of label: (regular expression, address, name)
    knowl_annotation_urls = [
        (r"example\.(\d+)", "Example/{0}", "Example {0}"),
    ]

    # The color scheme (see website/colors.py)
    @property
    def default_color(self):
        from .colors import SiteColors
        return SiteColors.code

    def color_schemes(self):
        from lmfdb_utils.color import all_color_schemes
        from .colors import SiteColors
        return {**all_color_schemes, SiteColors.code: SiteColors()}

    @property
    def db(self):
        from . import db
        return db


def grant_policy():
    """
    The privileges given on the tables the website creates (see
    psycodict.grants): the website's role can read the data and save
    statistics.
    """
    from psycodict.grants import GrantPolicy
    return GrantPolicy({
        "search": {"SELECT": [WEB_ROLE]},
        "counts": {"SELECT": [WEB_ROLE], "INSERT": [WEB_ROLE]},
        "stats": {"SELECT": [WEB_ROLE], "INSERT": [WEB_ROLE]},
        "meta": {"SELECT": [WEB_ROLE]},
        "meta_hist": {"SELECT": [WEB_ROLE]},
        "meta_format": {"SELECT": [WEB_ROLE]},
    }, missing_role="skip")
