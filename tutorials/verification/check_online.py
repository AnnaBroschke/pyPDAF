"""Compare output of an online tutorial with Fortran reference files.

All reference files (forecast and analysis of all steps) of the given
fields are compared. Usage (from the tutorials directory)::

    python verification/check_online.py <rundir> <refname>

e.g. ``python verification/check_online.py online_2D_serialmodel online_2D_serialmodel``
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
    parser.add_argument('--fields', nargs='+', default=['ens', 'state'],
                        help='file prefixes to compare, either "prefix" or '
                             '"run_prefix:ref_prefix" (default: ens state). '
                             'Example for the 2fields tutorial: ensA:ens stateA:state')
    args = parser.parse_args()
    refdir = os.path.join(os.path.dirname(__file__), args.refname)

    # The PDAF reference directories may also contain files of the 2fields
    # tutorial (ensB_*, stateB_*), therefore only the given prefixes are used.
    pairs = []   # (reference file, file name in run directory)
    for item in args.fields:
        run_prefix, _, ref_prefix = item.partition(':')
        ref_prefix = ref_prefix or run_prefix
        for ref in sorted(glob.glob(os.path.join(refdir, f'{ref_prefix}_*step*.txt'))):
            fname = run_prefix + os.path.basename(ref)[len(ref_prefix):]
            pairs.append((ref, fname))
    reffiles = [ref for ref, _ in pairs]
    maxdiff, worst, missing = 0.0, '', []
    for ref, fname in pairs:
        path = os.path.join(args.rundir, fname)
        if not os.path.exists(path):
            missing.append(fname)
            continue
        mdiff = np.max(np.abs(np.loadtxt(path) - np.loadtxt(ref)))
        if mdiff >= maxdiff:
            maxdiff, worst = mdiff, fname

    if missing:
        print(f'{len(missing)} of {len(reffiles)} files missing, e.g. {missing[0]}')
    status = 'OK' if (maxdiff < LIMIT and not missing) else 'WARNING!'
    print(f'Check {maxdiff:10.2e}   {args.rundir} vs {args.refname}: '
          f'{len(reffiles) - len(missing)} files, max. in {worst}  {status}')
