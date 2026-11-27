"""Compare analysis output of an offline tutorial with Fortran reference files.

Usage (from the tutorials directory)::

    python verification/check_offline.py <rundir> <refname>

e.g. ``python verification/check_offline.py offline_2D_serial offline_2D_serial``
compares ``offline_2D_serial/*_ana.txt`` with
``verification/offline_2D_serial/*_ana.txt`` (copied from PDAF/tutorial/verification).
"""
import argparse
import glob
import os

import numpy as np

LIMIT = 1.e-9

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('rundir')
    parser.add_argument('refname')
    args = parser.parse_args()
    refdir = os.path.join(os.path.dirname(__file__), args.refname)

    # All files of the reference directory are compared (10 for the
    # ensemble methods, 2 for parameterized 3D-Var with dim_ens=1)
    fnames = sorted(os.path.basename(f) for f in glob.glob(os.path.join(refdir, '*_ana.txt')))
    maxdiff, worst = 0.0, ''
    for fname in fnames:
        field = np.loadtxt(os.path.join(args.rundir, fname))
        field_ref = np.loadtxt(os.path.join(refdir, fname))
        mdiff = np.max(np.abs(field - field_ref))
        if mdiff >= maxdiff:
            maxdiff, worst = mdiff, fname

    status = 'OK' if maxdiff < LIMIT else 'WARNING!'
    print(f'Check {maxdiff:10.2e}   {args.rundir} vs {args.refname}: '
          f'{len(fnames)} files, max. in {worst}  {status}')
