# -*- coding: utf-8 -*-

"""User interface for command line script

"""

import argparse

from .core import process_backup


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-dir", help="Input directory", 
            required=True)
    parser.add_argument("-o", "--output-dir", help="Output directory", 
            required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    process_backup(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
