#!/usr/bin/env python3
"""Plot a 2D field of observations (missing values -999 are left blank).

Based on PDAF/tutorial/plotting/plot_obs.py. Requires Matplotlib and NumPy.

Usage: ./plot_obs.py <filename> [--save FILE.png]
"""
import argparse as ap
import os

import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma

from plot_utils import (CMAP_FIELD, describe, read_field, show_field,
                        show_or_save, sym_limit)


def read_and_plot(filename, save=None):
    field = read_field(filename)
    # As in the original script: only values in [-10, 10] are valid
    field_m = ma.masked_outside(field, -10.0, 10.0)
    nobs = int(field_m.count())

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_facecolor('#eeeeee')          # grid points without observation
    img = show_field(ax, field_m, CMAP_FIELD, sym_limit(field_m))
    ax.set_title(f'{describe(filename)} ({nobs} observations)\n'
                 f'{os.path.basename(filename)}', fontsize=11)
    fig.colorbar(img, ax=ax, label='Observed value', shrink=0.85)
    show_or_save(save, os.path.basename(filename).replace('.txt', '.png'))


if __name__ == "__main__":
    parser = ap.ArgumentParser(description='Plot an observation field of the tutorials.')
    parser.add_argument('filename')
    parser.add_argument('--save', metavar='FILE', default=None,
                        help='save figure to FILE (PNG) instead of showing it')
    args = parser.parse_args()
    try:
        read_and_plot(args.filename, args.save)
    except OSError as err:
        print(err)
