#!/usr/bin/env python
"""
Load the data of the example section (website/sections/example): for each
n up to a bound, the ways of writing n as a sum of two squares.  Also loads
the knowls the section uses (knowls/example.yaml) and computes the
statistics shown at /Example/stats.

Run it as the role owning the database, after scripts/init_db.py:

    sage -python scripts/load_example.py --config-file owner.ini

Use it as a model for loading your own data: create the table once with
db.create_table, then add rows with insert_many (or, for large data, write a
file and use copy_from or reload; see the psycodict documentation).
"""

import os

from _common import ROOT, parser, use_config

p = parser("Load the data of the example section")
p.add_argument("--bound", type=int, default=2000, help="load n from 1 to this bound [default: %(default)s]")
p.add_argument("--reload", action="store_true", help="drop and recreate the table first")
args = p.parse_args()
use_config(args)

from website import db  # noqa: E402

TABLE = "example_sums"


def factor(n):
    """
    The factorization of n, as a list of pairs [p, e]
    """
    factors = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            factors.append([p, e])
        p += 1
    if n > 1:
        factors.append([n, 1])
    return factors


def representations(n):
    """
    The pairs [x, y] with 0 <= x <= y and x^2 + y^2 = n
    """
    reps = []
    x = 0
    while 2 * x * x <= n:
        y2 = n - x * x
        y = int(round(y2 ** 0.5))
        while y * y > y2:
            y -= 1
        while (y + 1) * (y + 1) <= y2:
            y += 1
        if y * y == y2:
            reps.append([x, y])
        x += 1
    return reps


def r2(reps):
    """
    The number of pairs of integers (x, y), counting signs and order, with
    x^2 + y^2 = n, from the representations with 0 <= x <= y
    """
    total = 0
    for x, y in reps:
        signs = (1 if x == 0 else 2) * (1 if y == 0 else 2)
        total += signs * (1 if x == y else 2)
    return total


def record(n):
    reps = representations(n)
    factorization = factor(n)
    return {
        "label": str(n),
        "n": n,
        "r2": r2(reps),
        "reps": reps,
        "num_reps": len(reps),
        "factorization": factorization,
        "omega": len(factorization),
        "squarefree": all(e == 1 for p, e in factorization),
    }


if args.reload and TABLE in db.tablenames:
    db.drop_table(TABLE, force=True)
if TABLE not in db.tablenames:
    db.create_table(
        TABLE,
        {
            "text": ["label"],
            "integer": ["n", "r2"],
            "smallint": ["num_reps", "omega"],
            "jsonb": ["reps", "factorization"],
            "boolean": ["squarefree"],
        },
        label_col="label",
        sort=["n"],
    )
    table = db[TABLE]
    table.insert_many([record(n) for n in range(1, args.bound + 1)])
    table.create_index(["n"])
    table.create_index(["r2", "n"])
    print("Loaded %s rows into %s" % (table.count(), TABLE))
else:
    print("%s exists already (use --reload to recreate it)" % TABLE)

# The knowls used by the example section
from lmfdb_utils.knowledge.knowl import knowldb  # noqa: E402
knowldb.yaml_import(os.path.join(ROOT, "knowls", "example.yaml"), who="template", straight_to_production=True)

# The statistics shown at /Example/stats, which the website (whose role can
# only read the table) cannot compute itself
from website.app import app  # noqa: E402
from website.sections.example.main import ExampleStats  # noqa: E402
with app.app_context():
    stats = ExampleStats()
    stats.setup(delete=True)
    db[TABLE].stats.refresh_stats()
print("Computed the statistics of %s" % TABLE)
