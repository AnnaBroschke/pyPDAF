"""Initialise the ensemble (translation of offline_2D_parallel/init_ens_offline.F90).

Each process reads the full ensemble files, but stores only its own part of
the state vector (domain decomposition, see initialize.py).
"""
import numpy as np

import mod_assimilation as assim
import mod_model_pdaf as model
import mod_parallel_pdaf as par


def init_ens_offline(filtertype: int, dim_p: int, dim_ens: int,
                     state_p: np.ndarray, uinv: np.ndarray,
                     ens_p: np.ndarray, flag: int):
    """Read the ensemble and keep the process-local part."""
    if par.mype_filter == 0:
        print('\n' + ' ' * 9 + 'Initialize state ensemble')
        print(' ' * 9 + '--- read ensemble from files')
        print(' ' * 9 + f'--- Ensemble size:  {dim_ens:5d}')

    # Offset of the local part in the global state vector
    off_p = model.offset(par.mype_filter)

    for member in range(dim_ens):
        field = np.loadtxt(f'../inputs_offline/ens_{member + 1}.txt')
        state = field.ravel(order='F')               # global state vector
        assert state.size == assim.dim_state
        ens_p[:, member] = state[off_p:off_p + dim_p]  # local part

    return state_p, uinv, ens_p, flag
