# -*- coding: utf-8 -*-

import sys


def main():
    from .ui import main as realmain

    sys.exit(realmain())


if __name__ == "__main__":
    main()
