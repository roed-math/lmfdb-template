"""
The colors of the website.

The style sheet (/style.css, from lmfdb-utils) takes its colors from a color
scheme (a subclass of lmfdb_utils.color.ColorScheme).  SiteColors below is
the website's own; change its colors to change the look of the site.  Most of the other colors in the style sheet are derived
from these (see ColorScheme.colors in lmfdb_utils/color.py for the full list,
and the color schemes of the LMFDB defined there for examples).

Users can preview any scheme by adding ?color=<code> to an address, and
choose one on their account page (/users/myself) once logged in.
"""

from lmfdb_utils.color import YellowKnowls


class SiteColors(YellowKnowls):
    # The number identifying this scheme (the LMFDB's use 0-30)
    code = 100

    col_main_d = "#1B3A4B"   # header and footer background
    col_main_dl = "#3E7CB1"  # header and footer text
    col_main = "#1B3A4B"     # links and headings
    col_main_2 = "#8DB3D1"   # links when hovered
    col_main_l = "#C7DCEC"   # tabs and buttons
    col_main_lg = "#6C9AC3"  # shadows and borders of boxes
    col_main_ld = "#E3EEF6"  # background of boxes (properties, search forms)
    col_main_ll = "#F2F7FB"  # light background (beta notices, table rows)
    body_text = "#222222"
    col_link = "#2C6E9B"     # links in the text of pages
    col_a_knowl = "#2C6E9B"  # links in knowls

    # Knowls (the definitions that open when a term is clicked): the
    # YellowKnowls scheme sets their background and borders; these are
    # the color of the clickable terms and of the shadow of open knowls
    knowl_hyper_text = "#1F6F43"
    knowl_shadow = "#BBB"
