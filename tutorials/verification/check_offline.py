"""Compare analysis output of an offline tutorial with Fortran reference files.

Usage (from the tutorials directory)::

    python verification/check_offline.py <rundir> <refname>

e.g. ``python verification/check_offline.py offline_2D_serial offline_2D_serial``
compares ``offline_2D_serial/*_ana.txt`` with
``verification/offline_2D_serial/*_ana.txt`` (copied from PDAF/tutorial/verification).
"""
import argparse
import os

import numpy as np

LIMIT = 1.e-9

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('rundir')
    parser.add_argument('refname')
    args = parser.parse_args()
    refdir = os.path.join(os.path.dirname(__file__), args.refname)

    maxdiff, imax = 0.0, 0
    for i in range(10):
        fname = 'state_ana.txt' if i == 0 else f'ens_{i:02d}_ana.txt'
        field = np.loadtxt(os.path.join(args.rundir, fname))
        field_ref = np.loadtxt(os.path.join(refdir, fname))
        mdiff = np.max(np.abs(field - field_ref))
        if mdiff > maxdiff:
            maxdiff, imax = mdiff, i

    status = 'OK' if maxdiff < LIMIT else 'WARNING!'
    print(f'Check {maxdiff:10.2e}   {args.rundir} vs {args.refname} '
          f'at member {imax:3d}  {status}')
