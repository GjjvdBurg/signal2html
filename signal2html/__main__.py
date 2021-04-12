# -*- coding: utf-8 -*-

"""Command line interface

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: 2020, G.J.J. van den Burg
"""

import sys


def main():
    from .ui import main as realmain

    sys.exit(realmain())


if __name__ == "__main__":
    main()
