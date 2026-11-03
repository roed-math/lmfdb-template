#!/usr/bin/env python
"""
Run the website with Flask's development server:

    sage -python start-site.py --debug

then open http://127.0.0.1:37778 in a browser.  In production, run it with
gunicorn instead (see docs/DEPLOYING.md).
"""

import argparse

parser = argparse.ArgumentParser(description="Run the website (development server)")
parser.add_argument("--host", default="127.0.0.1", help="address to listen on [default: %(default)s]")
parser.add_argument("--port", type=int, default=37778, help="port to listen on [default: %(default)s]")
parser.add_argument("--debug", action="store_true",
                    help="debug mode: show errors in the browser, reload when the code changes, "
                         "and show content awaiting review (beta)")
args = parser.parse_args()

from website.app import app  # noqa: E402

app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=args.debug)
