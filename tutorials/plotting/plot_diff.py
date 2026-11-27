#!/usr/bin/env python3
"""Plot the difference of two 2D fields and print the RMSE.

Typical use: analysis minus truth. Based on PDAF/tutorial/plotting/plot_diff.py.
Requires Matplotlib and NumPy.

Usage: ./plot_diff.py <filename1> <filename2> [--save FILE.png]
"""
import argparse as ap
import os

import matplotlib.pyplot as plt
import numpy as np

from plot_utils import (CMAP_DIFF, describe, read_field, show_field,
                        show_or_save, sym_limit)


def read_and_plot(filename1, filename2, save=None):
    field1 = read_field(filename1)
    field2 = read_field(filename2)
    diff = field1 - field2

    # Root mean square difference over all grid points
    rmse = np.sqrt(np.mean(diff**2))
    print('RMSE: ', rmse)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    img = show_field(ax, diff, CMAP_DIFF, sym_limit(diff))
    ax.set_title(f'{describe(filename1)} minus {describe(filename2).lower()}\n'
                 f'{os.path.basename(filename1)} - {os.path.basename(filename2)}'
                 f'   (RMSE = {rmse:.4f})', fontsize=11)
    fig.colorbar(img, ax=ax, label='Difference', shrink=0.85)
    show_or_save(save, 'diff.png')


if __name__ == "__main__":
    parser = ap.ArgumentParser(description='Plot the difference of two 2D fields.')
    parser.add_argument('filename1')
    parser.add_argument('filename2')
    parser.add_argument('--save', metavar='FILE', default=None,
                        help='save figure to FILE (PNG) instead of showing it')
    args = parser.parse_args()
    try:
        read_and_plot(args.filename1, args.filename2, args.save)
    except OSError as err:
        print(err)
