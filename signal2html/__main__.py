# -*- coding: utf-8 -*-

"""Command line interface

License: See LICENSE file.
"""


def main():
    import logging
    import sys

    from .ui import main

    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s | %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    sys.exit(main())


if __name__ == "__main__":
    main()
