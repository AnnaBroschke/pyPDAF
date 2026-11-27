#!/usr/bin/env python3
"""Plot a 2D field of the tutorials (e.g. state, ensemble member, truth).

Based on PDAF/tutorial/plotting/plot_file.py. Requires Matplotlib and NumPy.

Usage: ./plot_file.py <filename> [--save FILE.png]
"""
import argparse as ap
import os

import matplotlib.pyplot as plt

from plot_utils import (CMAP_FIELD, describe, read_field, show_field,
                        show_or_save, sym_limit)


def read_and_plot(filename, save=None):
    field = read_field(filename)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    img = show_field(ax, field, CMAP_FIELD, sym_limit(field))
    ax.set_title(f'{describe(filename)}\n{os.path.basename(filename)}', fontsize=11)
    fig.colorbar(img, ax=ax, label='Field value', shrink=0.85)
    show_or_save(save, os.path.basename(filename).replace('.txt', '.png'))


if __name__ == "__main__":
    parser = ap.ArgumentParser(description='Plot a 2D field of the tutorials.')
    parser.add_argument('filename')
    parser.add_argument('--save', metavar='FILE', default=None,
                        help='save figure to FILE (PNG) instead of showing it')
    args = parser.parse_args()
    try:
        read_and_plot(args.filename, args.save)
    except OSError as err:
        print(err)
