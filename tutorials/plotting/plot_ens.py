#!/usr/bin/env python3
"""Plot a time series of ensemble mean and spread at one grid point.

For the online tutorials. Reads ``<prefix>_XX_stepYY_for.txt`` and
``<prefix>_XX_stepYY_ana.txt`` from the current directory. The analysis
steps are taken from the files, so any value of delt_obs works.
Based on PDAF/tutorial/plotting/plot_ens.py. Requires Matplotlib and NumPy.

Usage: ./plot_ens.py <i> <j> [--prefix ensB] [--save FILE.png]
       i, j: row and column index of the field (0-based, as in the original
       script). This is grid point x = j+1, y = i+1.
"""
import argparse as ap
import glob
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

from plot_utils import read_field, show_or_save


def read_ensemble(prefix, i, j):
    """Return analysis steps and the ensemble values at (i, j).

    Returns
    -------
    steps : (nsteps,) int
    ens : (nsteps, 2, nens) values at the point; [:, 0] forecast, [:, 1] analysis
    """
    files = glob.glob(f'{prefix}_01_step*_for.txt')
    steps = sorted(int(re.search(r'_step(\d+)_for', f).group(1)) for f in files)
    nens = len(glob.glob(f'{prefix}_*_step{steps[0]:02d}_for.txt')) if steps else 0
    if not steps or nens == 0:
        raise FileNotFoundError(f'No files {prefix}_XX_stepYY_for.txt found.')

    ens = np.empty((len(steps), 2, nens))
    for k, step in enumerate(steps):
        for m in range(nens):
            for p, phase in enumerate(('for', 'ana')):
                ens[k, p, m] = read_field(
                    f'{prefix}_{m + 1:02d}_step{step:02d}_{phase}.txt')[i, j]
    return np.array(steps), ens


def plot(steps, ens, i, j, prefix, save=None):
    # Forecast and analysis at the same time step -> two points per step
    time = np.repeat(steps, 2)
    values = ens.reshape(-1, ens.shape[-1])
    mean = values.mean(axis=-1)
    std = values.std(axis=-1)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.fill_between(time, mean - std, mean + std, color='C0', alpha=0.2,
                    linewidth=0, label='Ensemble mean ± 1 std. dev.')
    ax.plot(time, mean, color='C0', linewidth=2, label='Ensemble mean')
    ax.plot(steps, ens[:, 0].mean(axis=-1), 'o', color='C0', markersize=7,
            markerfacecolor='white', label='Forecast')
    ax.plot(steps, ens[:, 1].mean(axis=-1), 'o', color='C0', markersize=7,
            label='Analysis')

    field = prefix[3:]
    ax.set_title(f'Ensemble at grid point x={j + 1}, y={i + 1} (i={i}, j={j})'
                 + (f', field {field}' if field else '')
                 + f'\n{ens.shape[-1]} members', fontsize=11)
    ax.set_xlabel('Time step')
    ax.set_ylabel('Field value')
    ax.set_xticks(steps)
    ax.grid(True, color='#dddddd', linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
    show_or_save(save, f'{prefix}_{i}_{j}.png')


if __name__ == "__main__":
    parser = ap.ArgumentParser(description='Plot ensemble mean and spread at one grid point.')
    parser.add_argument('i', type=int, help='row index (0-based), grid point y = i+1')
    parser.add_argument('j', type=int, help='column index (0-based), grid point x = j+1')
    parser.add_argument('--prefix', default='ens',
                        help='file prefix: ens (default), ensA or ensB (2fields tutorial)')
    parser.add_argument('--save', metavar='FILE', default=None,
                        help='save figure to FILE (PNG) instead of showing it')
    args = parser.parse_args()
    print("Plotting time series for point at i={0:d}, j={1:d}.".format(args.i, args.j))
    try:
        steps, ens = read_ensemble(args.prefix, args.i, args.j)
    except Exception as err:
        print(err)
        sys.exit(1)

    plot(steps, ens, args.i, args.j, args.prefix, args.save)
