"""Initialise the ensemble (translation of 3dvar/offline_2D_serial/init_ens_offline.F90).

Call-back routine called by PDAF3_init for the ensemble and hybrid 3D-Var
(subtype 1-4). The ensemble is read from ``../../inputs_offline/ens_X.txt``.
For filtertype 200, B^1/2 (Vmat_p) for the parameterized part of hybrid
3D-Var is computed from the same ensemble.
"""
import numpy as np

import mod_assimilation as assim


def init_ens_offline(filtertype: int, dim_p: int, dim_ens: int,
                     state_p: np.ndarray, uinv: np.ndarray,
                     ens_p: np.ndarray, flag: int):
    """Read the ensemble from files and return the filled arrays."""
    print('\n' + ' ' * 9 + 'Initialize state ensemble')
    print(' ' * 9 + '--- read ensemble from files')
    print(' ' * 9 + f'--- Ensemble size:  {dim_ens:5d}')

    invdim_ens = 1.0 / assim.dim_cvec

    for member in range(dim_ens):
        field = np.loadtxt(f'../../inputs_offline/ens_{member + 1}.txt')
        assert field.shape == (assim.ny, assim.nx)
        ens_p[:, member] = field.ravel(order='F')

    # *** B^1/2 for the parameterized part of hybrid 3D-Var ***
    if filtertype == 200:
        print(' ' * 9 + 'Initialize B^1/2 for 3D-Var')
        state_p[:] = 0.0
        for member in range(assim.dim_cvec):      # same summation order as Fortran
            state_p[:] += ens_p[:, member]
        state_p[:] = invdim_ens * state_p

        assim.Vmat_p = np.zeros((dim_p, assim.dim_cvec), order='F')
        for member in range(dim_ens):
            assim.Vmat_p[:, member] = ens_p[:, member] - state_p

        fact = 1.0 / np.sqrt(assim.dim_cvec - 1)
        assim.Vmat_p *= fact

    return state_p, uinv, ens_p, flag
