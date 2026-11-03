"""
What the scripts share: choosing the configuration file before the website
package connects to the database.
"""

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def parser(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument(
        "-c", "--config-file",
        help="the configuration file to connect with, normally one for the role "
             "owning the database [default: $SITE_CONFIG, or config.ini]",
    )
    return p


def use_config(args):
    """
    Make the website connect with the configuration file given on the command
    line (by setting SITE_CONFIG before website.config reads it).
    """
    if args.config_file:
        os.environ["SITE_CONFIG"] = os.path.abspath(args.config_file)
