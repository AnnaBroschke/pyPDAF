"""Initialise the ensemble (translation of 3dvar/online_2D_serialmodel/init_ens_pdaf.F90).

Call-back routine called by PDAF3_init. Reads the ensemble members from
``../../inputs_online/ens_X.txt`` (ensgroup=1) or ``ensB_X.txt`` (ensgroup=2).
The 2D field is stored column-wise in the state vector (``order='F'``).
For hybrid 3D-Var (subtype 3, 4), B^1/2 (Vmat_p) for the parameterized part
is computed from the same ensemble.
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

    invdim_ens = 1.0 / assim.dim_cvec

    prefix = 'ens' if assim.ensgroup == 1 else 'ensB'
    for member in range(dim_ens):
        field = np.loadtxt(f'../../inputs_online/{prefix}_{member + 1}.txt')
        assert field.shape == (model.ny, model.nx)
        ens_p[:, member] = field.ravel(order='F')

    # *** B^1/2 for the parameterized part of 3D-Var ***
    if filtertype == 200 and assim.subtype in (0, 3, 4):
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
