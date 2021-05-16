# -*- coding: utf-8 -*-

"""Command line interface

License: See LICENSE file.
"""

import sys
import logging


def main():
    from .ui import main as realmain

    sys.exit(realmain())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
