#!/usr/bin/env python3

# A script to plot the 2D field from the online_2D_serialmodel tutorial.
# Requires Python 3, Matplotlib and Numpy.

# Usage: ./plot_field.py <filename>

import matplotlib.pyplot as plt
import numpy as np
import argparse as ap

import os

def show_or_save(save, default_name):
    """Show the figure, or save it as PNG if --save is given or no display is available."""
    if save is None and not os.environ.get('DISPLAY'):
        save = default_name
    if save:
        plt.savefig(save, dpi=150, bbox_inches='tight')
        print('Figure saved to', save)
    else:
        plt.show()

def read_and_plot(filename, save=None):
    field = np.loadtxt(filename)
    field = field.reshape(18,36)
    plt.imshow(field, origin='lower',interpolation='none')
    plt.title(filename)
    plt.colorbar()
    show_or_save(save, os.path.basename(filename).replace('.txt', '.png'))

if __name__ == "__main__":
    parser = ap.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--save', metavar='FILE', default=None,
                        help='save figure to FILE (PNG) instead of showing it')
    args = parser.parse_args()
    try:
        read_and_plot(args.filename, args.save)
    except OSError as err:
        print(err)
