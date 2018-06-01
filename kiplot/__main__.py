# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

from . import kiplot
from . import config_reader


def main():

    parser = argparse.ArgumentParser(
        description='Command-line Plotting for KiCad')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='show debugging information')
    parser.add_argument('-b', '--board-file', required=True,
                        help='The PCB .kicad-pcb board file')
    parser.add_argument('-c', '--plot-config', required=True,
                        help='The plotting config file to use')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    if not os.path.isfile(args.board_file):
        logging.error("Board file not found: {}".format(args.board_file))

    if not os.path.isfile(args.plot_config):
        logging.error("Plot config file not found: {}"
                      .format(args.plot_config))

    cr = config_reader.CfgYamlReader()

    with open(args.plot_config) as cf_file:
        cfg = cr.read(cf_file)

    plotter = kiplot.Plotter(cfg)

    plotter.plot(args.board_file)


if __name__ == "__main__":
    main()
