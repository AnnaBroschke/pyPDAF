"""Initialise the ensemble (translation of init_ens_pdaf.F90).

Call-back routine called by PDAF3_init. For each member, field A is read
from ``ens_X.txt`` and field B from ``ensB_X.txt`` and stored at the
position of the field in the state vector (see mod_statevector_pdaf.py).
"""
import numpy as np

import mod_model as model
from mod_statevector_pdaf import id, sfields


def init_ens_pdaf(filtertype: int, dim_p: int, dim_ens: int,
                  state_p: np.ndarray, uinv: np.ndarray,
                  ens_p: np.ndarray, flag: int):
    """Read the ensemble of both fields and return the filled arrays."""
    print('\n' + ' ' * 9 + 'Initialize state ensemble')
    print(' ' * 9 + '--- read ensemble from files')
    print(' ' * 9 + f'--- Ensemble size:  {dim_ens:5d}')

    for member in range(dim_ens):
        for fid, prefix in ((id.fieldA, 'ens'), (id.fieldB, 'ensB')):
            readfield = np.loadtxt(f'../inputs_online_2fields/{prefix}_{member + 1}.txt')
            assert readfield.shape == (model.ny, model.nx)
            ens_p[sfields[fid].slice, member] = readfield.ravel(order='F')

    return state_p, uinv, ens_p, flag
