"""Initialise the ensemble (translation of 3dvar/online_2D_parallelmodel/init_ens_pdaf.F90).

Each filter process reads the ensemble and keeps its nx_p columns. For
hybrid 3D-Var (subtype 3, 4) the local rows of B^1/2 (Vmat_p) are computed
from the same ensemble.
"""
import numpy as np

import mod_assimilation as assim
import mod_model as model
import mod_parallel_model as pm
import mod_parallel_pdaf as par


def init_ens_pdaf(filtertype: int, dim_p: int, dim_ens: int,
                  state_p: np.ndarray, uinv: np.ndarray,
                  ens_p: np.ndarray, flag: int):
    """Read the ensemble and keep the process-local columns."""
    if par.mype_filter == 0:
        print('\n' + ' ' * 9 + 'Initialize state ensemble')
        print(' ' * 9 + '--- read ensemble from files')
        print(' ' * 9 + f'--- Ensemble size:  {dim_ens:5d}')

    j0 = model.nx_p * pm.mype_2Dmodel
    for member in range(dim_ens):
        field = np.loadtxt(f'../../inputs_online/ens_{member + 1}.txt')
        ens_p[:, member] = field[:, j0:j0 + model.nx_p].ravel(order='F')

    if filtertype == 200 and assim.subtype in (0, 3, 4):
        print(' ' * 9 + 'Initialize B^1/2 for 3D-Var')
        invdim_ens = 1.0 / assim.dim_cvec
        state_p[:] = 0.0
        for member in range(assim.dim_cvec):
            state_p[:] += ens_p[:, member]
        state_p[:] = invdim_ens * state_p
        assim.Vmat_p = np.zeros((dim_p, assim.dim_cvec), order='F')
        for member in range(dim_ens):
            assim.Vmat_p[:, member] = ens_p[:, member] - state_p
        assim.Vmat_p *= 1.0 / np.sqrt(assim.dim_cvec - 1)

    return state_p, uinv, ens_p, flag
