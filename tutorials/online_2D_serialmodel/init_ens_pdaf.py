"""Initialise the ensemble (translation of init_ens_pdaf.F90).

Call-back routine called by PDAF3_init. Reads the ensemble members from
``../inputs_online/ens_X.txt`` (ensgroup=1) or ``ensB_X.txt`` (ensgroup=2).
The 2D field is stored column-wise in the state vector (``order='F'``).
"""
import numpy as np

import mod_assimilation as assim
import mod_model as model


def init_ens_pdaf(filtertype: int, dim_p: int, dim_ens: int,
                  state_p: np.ndarray, uinv: np.ndarray,
                  ens_p: np.ndarray, flag: int):
    """Read the ensemble from files and return the filled arrays."""
    print('\n' + ' ' * 9 + 'Initialize state ensemble')
    print(' ' * 9 + '--- read ensemble from files')
    print(' ' * 9 + f'--- Ensemble size:  {dim_ens:5d}')

    prefix = 'ens' if assim.ensgroup == 1 else 'ensB'
    for member in range(dim_ens):
        field = np.loadtxt(f'../inputs_online/{prefix}_{member + 1}.txt')
        assert field.shape == (model.ny, model.nx)
        ens_p[:, member] = field.ravel(order='F')

    return state_p, uinv, ens_p, flag
