# -*- coding: utf-8 -*-

import argparse
import logging

from . import kiplot


def main():

    parser = argparse.ArgumentParser(description='Command-line Plotting for KiCad')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='show debugging information')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)


if __name__ == "__main__":
    main()
    