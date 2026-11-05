"""
The pages of the example section: browsing and searching, a page for each n,
random n, downloads and statistics.

The data is in the table example_sums (see scripts/load_example.py), with
columns

- label (text): n, as a string;
- n (integer);
- r2 (integer): the number of pairs of integers (x, y) with x^2 + y^2 = n;
- reps (jsonb): the pairs [x, y] with 0 <= x <= y and x^2 + y^2 = n;
- num_reps (smallint): their number;
- factorization (jsonb): the factorization of n, as pairs [p, e];
- omega (smallint): the number of distinct prime factors of n;
- squarefree (boolean): whether n is squarefree.

The knowls used below (example.*) are in knowls/example.yaml.
"""

import re

from flask import redirect, render_template, request, url_for

from lmfdb_utils.display_stats import StatsDisplay, proportioners, totaler
from lmfdb_utils.downloader import Downloader
from lmfdb_utils.lazy import LazyObject
from lmfdb_utils.random_wrap import redirect_no_cache
from lmfdb_utils.search_boxes import CountBox, SearchArray, TextBox, YesNoBox
from lmfdb_utils.search_columns import CheckCol, LinkCol, MathCol, ProcessedCol, SearchColumns
from lmfdb_utils.search_parsing import clean_input, parse_bool, parse_ints
from lmfdb_utils.search_wrapper import search_wrap
from lmfdb_utils.utilities import comma, flash_error, to_dict
from lmfdb_utils.web_display import display_knowl

from website import db
from . import example_page

# Looked up when first used, so that the website starts (and shows an error
# here) before the example data has been loaded
table = LazyObject(lambda: db.example_sums, "The table example_sums")

LABEL_RE = re.compile(r"^\d+$")


def get_bread(*breads):
    return [("Sums of two squares", url_for(".index"))] + list(breads)


def learnmore_list():
    return [("Source of the data", url_for(".source")),
            ("Labels", url_for(".labels"))]


##############################
#      Formatting            #
##############################

def show_reps(reps):
    return ", ".join("$%s^2 + %s^2$" % (x, y) for x, y in reps) or "none"


def show_factorization(factorization):
    if not factorization:
        return "$1$"
    return "$" + r" \cdot ".join(str(p) if e == 1 else "%s^{%s}" % (p, e) for p, e in factorization) + "$"


##############################
#      Browse and search     #
##############################

@example_page.route("/")
def index():
    info = to_dict(request.args, search_array=ExampleSearchArray())
    if request.args:
        return example_search(info)
    info["stats"] = ExampleStats()
    info["n_list"] = ["1-100", "101-1000", "1001-2000"]
    return render_template("example-index.html", info=info, title="Sums of two squares",
                           bread=get_bread(), learnmore=learnmore_list())


@example_page.route("/random")
@redirect_no_cache
def random_n():
    return url_for(".by_label", label=table.random(projection="label"))


def url_for_label(label):
    if label == "random":
        return url_for(".random_n")
    return url_for(".by_label", label=label)


def jump(info):
    label = info["jump"].strip()
    if not LABEL_RE.match(label):
        flash_error("%s is not a positive integer", label)
        return redirect(url_for(".index"))
    return redirect(url_for(".by_label", label=label))


example_columns = SearchColumns([
    LinkCol("label", "example.n", "$n$", url_for_label),
    ProcessedCol("factorization", "example.factorization", "Factorization", show_factorization, align="center"),
    MathCol("r2", "example.r2", "$r_2(n)$"),
    MathCol("num_reps", "example.num_reps", "Representations"),
    ProcessedCol("reps", "example.representations", "$x^2 + y^2$", show_reps, default=False),
    MathCol("omega", "example.omega", r"$\omega(n)$", default=False),
    CheckCol("squarefree", "example.squarefree", "Squarefree"),
])


class ExampleDownloader(Downloader):
    # Given here, so that the table is not needed until a download happens
    title = "Sums of two squares"
    short_name = "sum"
    var_name = "sums"
    filebase = "sums_of_two_squares"


@search_wrap(
    table=table,
    title="Sums of two squares: search results",
    err_title="Sums of two squares: search input error",
    columns=example_columns,
    shortcuts={"jump": jump, "download": ExampleDownloader(table)},
    url_for_label=url_for_label,
    bread=lambda: get_bread(("Search results", " ")),
    learnmore=learnmore_list,
)
def example_search(info, query):
    parse_ints(info, query, "n")
    parse_ints(info, query, "r2")
    parse_ints(info, query, "num_reps")
    parse_ints(info, query, "omega")
    parse_bool(info, query, "squarefree")
    # "Sum of two squares" is also a condition on num_reps: parse it apart and
    # add it to the conditions already there (the parsers also use $and, for
    # negated inputs such as n=~25), rather than letting it replace them
    is_sum = {}
    parse_bool(info, is_sum, "is_sum", qfield="num_reps", process=lambda x: {"$gt": 0} if x else 0)
    if is_sum:
        query.setdefault("$and", []).append(is_sum)


class ExampleSearchArray(SearchArray):
    noun = "integer"
    plural_noun = "integers"
    jump_example = "65"
    jump_egspan = "e.g. 65 or 1105"
    sorts = [("", "n", ["n"]),
             ("r2", "number of representations", ["r2", "n"])]

    def __init__(self):
        n = TextBox(name="n", label="$n$", knowl="example.n",
                    example="1-100", example_span="65, or a range like 1-100")
        r2 = TextBox(name="r2", label="$r_2(n)$", knowl="example.r2",
                     example="8", example_span="8, or a range like 4-16")
        num_reps = TextBox(name="num_reps", label="Representations", knowl="example.num_reps",
                           example="2", example_span="2, or a range like 1-3")
        omega = TextBox(name="omega", label=r"$\omega(n)$", knowl="example.omega",
                        example="2", example_span="2, or a range like 1-3")
        is_sum = YesNoBox(name="is_sum", label="Sum of two squares", knowl="example.r2")
        squarefree = YesNoBox(name="squarefree", label="Squarefree", knowl="example.squarefree")
        count = CountBox()

        self.browse_array = [[n, is_sum], [r2, squarefree], [num_reps, omega], [count]]
        self.refine_array = [[n, r2, num_reps], [omega, is_sum, squarefree]]


##############################
#      Object pages          #
##############################

@example_page.route("/<label>")
def by_label(label):
    label = clean_input(label)
    data = table.lookup(label) if LABEL_RE.match(label) else None
    if data is None:
        flash_error("There is no integer %s in the database", label)
        return redirect(url_for(".index"))
    properties = [
        ("$n$", str(data["n"])),
        ("Factorization", show_factorization(data["factorization"])),
        ("$r_2(n)$", str(data["r2"])),
        ("Squarefree", "yes" if data["squarefree"] else "no"),
    ]
    n = data["n"]
    friends = []
    for m in (n - 1, n + 1):
        if m >= 1 and table.exists({"n": m}):
            friends.append(("Sums of two squares for %s" % m, url_for(".by_label", label=str(m))))
    return render_template(
        "example-show.html",
        data=data,
        reps=show_reps(data["reps"]),
        factorization=show_factorization(data["factorization"]),
        title="Sums of two squares equal to %s" % n,
        bread=get_bread((str(n), " ")),
        properties=properties,
        friends=friends,
        learnmore=learnmore_list(),
        KNOWL_ID="example.%s" % n,
    )


##############################
#      Statistics            #
##############################

class ExampleStats(StatsDisplay):
    """
    The statistics shown at /Example/stats.  The counts are stored in the
    tables example_sums_counts and example_sums_stats: scripts/load_example.py
    computes them, since the website's role cannot write them otherwise.
    """
    table = table
    baseurl_func = ".index"
    short_display = {"r2": "r_2(n)", "omega": "omega(n)"}
    top_titles = {"r2": "number of representations", "omega": "number of prime factors"}
    knowls = {"r2": "example.r2", "omega": "example.omega", "squarefree": "example.squarefree"}
    # the buckets must cover every value (the last one is open-ended)
    buckets = {"r2": ["0", "4", "8", "12", "16", "20", "24-32", "36-"]}
    # One-dimensional statistics (a single column) and two-dimensional ones
    # (a grid); see lmfdb_utils/display_stats.py for the options
    stat_list = [
        {"cols": "r2"},
        {"cols": "omega", "totaler": {"avg": True}},
        {"cols": ["omega", "squarefree"], "totaler": totaler(),
         "proportioner": proportioners.per_col_total},
    ]

    @property
    def summary(self):
        return "The database contains the %s integers from 1 to %s, of which %s are %s." % (
            comma(table.count()),
            comma(table.max("n")),
            comma(table.count({"num_reps": {"$gt": 0}})),
            display_knowl("example.r2", "sums of two squares"),
        )

    @property
    def short_summary(self):
        return self.summary + ' Here are some <a href="%s">further statistics</a>.' % url_for(".statistics")


@example_page.route("/stats")
def statistics():
    return render_template("display_stats.html", info=ExampleStats(), title="Sums of two squares: statistics",
                           bread=get_bread(("Statistics", " ")), learnmore=learnmore_list())


##############################
#      About the data        #
##############################

@example_page.route("/Source")
def source():
    return render_template("single.html", kid="rcs.example.source", title="Source of the data",
                           bread=get_bread(("Source", " ")), learnmore=learnmore_list())


@example_page.route("/Labels")
def labels():
    return render_template("single.html", kid="example.label", title="Labels",
                           bread=get_bread(("Labels", " ")), learnmore=learnmore_list())
